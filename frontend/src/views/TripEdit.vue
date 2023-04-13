<script setup>
import Layout from '../components/Layout.vue';
import TripMethodsAPI from '../api/resources/TripMethods';
import { ref } from 'vue';
import router from '../router';
import TripMethods from '../api/resources/TripMethods';

const props = defineProps(['id']);

const trip = ref({});
const pin = ref("");
const data = ref({});

const trip_data = await TripMethodsAPI.get(props.id);
trip.value = trip_data;
data.value.date_from = trip_data.date_from;
data.value.date_to = trip_data.date_to;
data.value.markdown = trip_data.markdown;
data.value.participants = trip_data.participants.map(item => item.user_id).join(',');

const saving = ref(false);
const save = async () => {
    saving.value = true;
    try {
        await TripMethodsAPI.update(props.id, pin.value, data.value);
        router.push({name: "trip_view", params: {id: props.id}});
    } catch (error) {
        alert("error - did you provide the correct edit code? and fill all fields correct?");
    }
    saving.value = false;
    return false;
}

const remove = async () => {
    try {
        await TripMethodsAPI.remove(props.id, pin.value);
        router.push({name: "home"});
    } catch(error) {
        alert("error - did you put the correct edit code?");
    }
    return false;
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
            <label for="date_from">Date from</label>
            <input type="date" id="date_from" v-model="data.date_from" pattern="\d{4}-\d{2}-\d{2}" />
            <label for="date_to">Date to</label>
            <input type="date" id="date_to" v-model="data.date_to" pattern="\d{4}-\d{2}-\d{2}" />
            <label for="markdown">Text/markdown</label>
            <textarea id="markdown" v-model="data.markdown"></textarea>
            <label for="participants">Participants</label>
            <input type="text" v-model="data.participants" />

            <label for="edit_code">Edit code (enter correct edit code to sync/save/delete)</label>
            <input type="text" id="edit_code" v-model="pin">
            <button class="button error" @click="remove">delete</button> <button class="button action" :disabled="resyncing" @click="resync">*resync 27crags</button> <button class="button" :disabled="saving" @click="save">save</button>
            <p>* Please dont't resync too often - it is a slow process (can take up to an hour)..... we resync automatic every 24 hours</p>
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