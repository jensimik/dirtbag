<script setup>
import TripMethodsAPI from '../api/resources/TripMethods';
import { ref } from 'vue';
import router from '../router';

const props = defineProps(['id', 'pin']);

const trip = ref({});
const trip_data = await TripMethodsAPI.get(props.id, props.pin);
trip.value = trip_data;

const save = async () => {
    console.log(trip.value.participants);
}

const remove = async (i) => {
    console.log(i);
    const index = trip.value.participants.indexOf(i);
    trip.value.participants.splice(index, 1);
}

const resyncing = ref(false);
const resync = async () => {
    resyncing.value = true;
    await TripMethodsAPI.resync(props.id, props.pin);
    await new Promise(r => setTimeout(r, 10000));
    resyncing.value = false;
}
</script>

<template>
    <h2>{{ trip.area_name }}</h2>

    <h3>Participants</h3>
    <div v-for="u, i in trip.participants" :key="u.thumb_url" class="flex grow">
        <div class="small"><input type="text" v-model="u.name" maxlength="3" placeholder="Initials" /></div>
        <div class="bigger">
            <input type="text" v-model="u.user_id" placeholder="27crags username" />
        </div>
        <div class="small"><button class="small button warn" @click="remove(u)">x</button></div>

    </div>
    <button class="button" @click="save">save</button>
    <h3>Resync 27crags data</h3>
    <p>Please dont't resync too often - it is a slow process (can take up to an hour).....</p>
    <button class="button action" :disabled="resyncing" @click="resync">resync 27crags</button>
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