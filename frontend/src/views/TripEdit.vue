<script setup>
import Layout from '../components/Layout.vue';
import TripMethodsAPI from '../api/resources/TripMethods';
import { ref } from 'vue';
import router from '../router';

const props = defineProps(['id']);

const trip = ref({});
const auth = ref(false);
const pin = ref("");
const data = ref({});

const get_trip = async () => {
    const trip_data = await TripMethodsAPI.get(props.id, pin.value);
    trip.value = trip_data;
    auth.value = true;
    data.value.date_from = trip_data.date_from;
    data.value.date_to = trip_data.date_to;
    data.markdown = trip_data.markdown;
    data.participants = trip_data.participants.map(item => item.user_id).join(',');
    data.pin = trip_data.pin;
}

const saving = ref(false);
const save = async () => {
    saving.value = true;
    await TripMethodsAPI.update(props.id, pin.value, data.value);
    router.push({name: "trip_view", params: {id: props.id}});
    saving.value = false;
}


const resyncing = ref(false);
const resync = async () => {
    resyncing.value = true;
    await TripMethodsAPI.resync(props.id, pin.value);
    await new Promise(r => setTimeout(r, 20000));
    resyncing.value = false;
}


</script>

<template>
    <Layout>
        <template v-slot:title>{{ trip.area_name }}</template>
        <template v-slot:content>
            <div v-if="auth">
                <label for="edit_code">Edit code</label>
                <input type="text" id="edit_code" v-model="data.pin">
                <label for="date_from">Date from</label>
                <input type="date" id="date_from" v-model="data.date_from" pattern="\d{4}-\d{2}-\d{2}" />
                <label for="date_to">Date to</label>
                <input type="date" id="date_to" v-model="data.date_to" pattern="\d{4}-\d{2}-\d{2}" />
                <label for="markdown">Text/markdown</label>
                <textarea id="markdown" v-model="data.markdown"></textarea>
                <label for="participants">Participants</label>
                <input type="text" v-model="data.participants" />
                <button class="button" :disabled="saving" @click="save">save</button>
                <h3>Resync 27crags data</h3>
                <p>Please dont't resync too often - it is a slow process (can take up to an hour).....</p>
                <button class="button action" :disabled="resyncing" @click="resync">resync 27crags</button>
            </div>
            <div v-else>
                <label for="password">Enter code</label>
                <input id="password" type="password" v-model="pin" />
                <button class="button" @click="get_trip">auth</button>
            </div>
        </template>
    </Layout>
</template>

<style scoped>
.small {
    flex-basis: 4em;
    flex-grow: 0;
}

.bigger {
    flex-basis: auto;
    flex-grow: 1;
}

/* input[type='text'] {
    width: 4em;
} */

img.thumb {
    width: 1.5em;
    height: 1.5em;
}
</style>