<script setup>
import Layout from '../components/Layout.vue';
import UserMethodsAPI from '../api/resources/UserMethods';
import TripMethodsAPI from '../api/resources/TripMethods';
import { ref } from 'vue';
import router from '../router';

const makeid = function(length) {
    let result = '';
    const characters = 'abcdefghijkmnpqrstuvwxyz23456789';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
      counter += 1;
    }
    return result;
}

const data = ref({ date_from: "", date_to: "", user_id: "", area_name: "", participants: "", "pin": makeid(4) });
const processing = ref(false);
const sync_text = ref("sync 27 crags");
const synced = ref(false);
const areas = ref([]);

const sync_27_crags = async () => {
    sync_text.value = 'working....'
    processing.value = true;
    await UserMethodsAPI.sync_27crags(data.value.user_id);
    const timer = setInterval(async () => {
        const status = await UserMethodsAPI.sync_done(data.value.user_id);
        if (!status.processing) {
            areas.value = await UserMethodsAPI.get_areas(data.value.user_id);
            data.value.participants = data.value.user_id;
            synced.value = true;
            clearInterval(timer);
            processing.value = false;
        }
    }, 10000);
}

const create_trip = async () => {
    processing.value = true;
    const new_id = await TripMethodsAPI.create(data.value);
    router.push({ name: 'trip_view', params: { id: new_id } })
}
</script>

<template>
    <Layout>
        <template v-slot:title>create trip</template>
        <template v-slot:content>
            <div class="flex one">
                <label for="date_from">Date from</label>
                <input type="date" id="date_from" v-model="data.date_from" pattern="\d{4}-\d{2}-\d{2}" />
                <label for="date_to">Date to</label>
                <input type="date" id="date_to" v-model="data.date_to" pattern="\d{4}-\d{2}-\d{2}" />
                <label for="user_id">27crags user_name</label>
                <input type="text" id="user_id" v-model="data.user_id" :readonly="processing"
                    placeholder="find username when logging in to 27crags in a browser and look in the url address" />
                <div class="flex two" v-if="!synced">
                    <div></div>
                    <div class="right"><button class="button" :disabled="processing || data.user_id.length < 1"
                            @click="sync_27_crags">{{
                                sync_text
                            }}</button>
                    </div>
                </div>
                <div v-if="synced">
                    <label for="area_name">Destination</label>
                    <select id="area_name" v-model="data.area_name">
                        <option :value="area.name" v-for="area in areas">{{ area.name }}</option>
                    </select>
                    <label for="crew">Crew</label>
                    <input type="text" id="crew" v-model="data.participants"
                        placeholder="enter a list of 27crags user_names seperated by comma fx.: jensda,strongdude,ondra" />
                    <label for="edit_code">Password to edit trip later (enter 4-10 letters)</label>
                    <input type="text" id="edit_code" v-model="data.pin">
                    <div class="flex two">
                        <div></div>
                        <div class="right"><button class="button" @click="create_trip" :disabled="processing">create</button>
                        </div>
                    </div>
                </div>
            </div>
        </template>
    </Layout>
</template>

<style scoped>
.right {
    text-align: right;
}
</style>