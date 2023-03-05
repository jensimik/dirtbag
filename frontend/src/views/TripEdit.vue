<script setup>
import Layout from '../components/Layout.vue';
import TripMethodsAPI from '../api/resources/TripMethods';
import { ref } from 'vue';
import router from '../router';

const props = defineProps(['id', 'pin']);

const trip = ref({});
const trip_data = await TripMethodsAPI.get(props.id, props.pin);
trip.value = trip_data;
const data = ref({ date_from: trip_data.date_from, date_to: trip_data.date_to, markdown: trip_data.markdown, participants: trip.value.participants.map(item => item.user_id).join(',') });

const saving = ref(false);
const save = async () => {
    saving.value = true;
    await TripMethodsAPI.update(props.id, props.pin, data.value);
    router.push({name: "trip_auth", params: {id: props.id, pin: props.pin}});
    saving.value = false;
}


const resyncing = ref(false);
const resync = async () => {
    resyncing.value = true;
    await TripMethodsAPI.resync(props.id, props.pin);
    await new Promise(r => setTimeout(r, 20000));
    resyncing.value = false;
}


</script>

<template>
    <Layout>
        <template v-slot:title>{{ trip.area_name }}</template>
        <template v-slot:content>
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