<script setup>
import TripMethodsAPI from '../api/resources/TripMethods';
import { ref } from 'vue';


const trips = ref([]);
trips.value = await TripMethodsAPI.index();
</script>

<template>
    <h2>Trips</h2>
    <div class="flex three" v-for=" trip in trips" :key="trip.id">
        <div><router-link :to="{ name: 'auth_trip', params: { id: trip.id } }">{{ trip.area_name }}</router-link></div>
        <div>{{ trip.date_from }} ({{ trip.duration ? trip.duration + ' days' : 'daytrip' }})</div>
        <div class="right">
            <img class="thumb" :src="user.thumb_url" :title="user.name" v-for="user in trip.participants"
                :key="user.id" />
        </div>
    </div>
</template>

<style scoped>
img.thumb {
    width: 1.5em;
    height: 1.5em;
    margin-left: 0.2em;
}

div.right {
    text-align: right;
    /* justify-content: flex-end; */
}
</style>