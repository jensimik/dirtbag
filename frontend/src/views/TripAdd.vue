<script setup>
import UserMethodsAPI from '../api/resources/UserMethods';
import { ref } from 'vue';

const data = ref({ date_from: "", date_to: "", user_id: "", area_name: "" });
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
            areas.value = await UserMethodsAPI.areas(data.value.user_id);
            synced.value = true;
            clearInterval(timer);
        }
    }, 10000);
}
</script>

<template>
    <h2>Create trip</h2>

    <div>
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
            <input type="text" id="crew"
                placeholder="enter a list of 27crags user_names seperated by comma fx.: jensda,strongdude,ondra" />
            <div class="flex two">
                <div></div>
                <div class="right"><button class="button">create</button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.right {
    text-align: right;
}
</style>