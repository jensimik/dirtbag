<script setup>
import Layout from '../components/Layout.vue';
import TripMethodsAPI from '../api/resources/TripMethods';
import { ref } from 'vue';

const getUniqueColor = (n) => {
    const rgb = [0, 0, 0];

    for (let i = 0; i < 24; i++) {
        rgb[i % 3] <<= 1;
        rgb[i % 3] |= n & 0x01;
        n >>= 1;
    }
    return '#' + rgb.reduce((a, c) => (c > 0x0f ? c.toString(16) : '0' + c.toString(16)) + a, '')
}

const trips = ref({});
trips.value = await TripMethodsAPI.index();
</script>

<template>
    <Layout>
        <template v-slot:menu>
            <router-link :to="{ name: 'trip_add' }" class="button">create</router-link>
        </template>
        <template v-slot:content>
            <h2>Current/Upcoming</h2>
            <div class="flex three" v-for=" trip in trips.current" :key="trip.id">
                <div><router-link :to="{ name: 'trip_view', params: { id: trip.id } }">{{ trip.area_name }}</router-link></div>
                <div>{{ trip.date_from_display }} -{{ trip.date_to_display }} ({{
                    trip.duration ? trip.duration + ' days' :
                        'daytrip'
                }})</div>
                <div class="right">
                    <span class="tag" :style="{ backgroundColor: getUniqueColor(i) }" v-for="(user, i) in trip.participants">{{
                        user.name
                    }}</span>
                </div>
            </div>
            <h2>History</h2>
            <div class="flex three" v-for=" trip in trips.past" :key="trip.id">
                <div><router-link :to="{ name: 'trip_view', params: { id: trip.id } }">{{ trip.area_name }}</router-link></div>
                <div>{{ trip.date_from_display }} -{{ trip.date_to_display }} ({{
                    trip.duration ? trip.duration + ' days' :
                        'daytrip'
                }})</div>
                <div class="right">
                    <span class="tag" :style="{ backgroundColor: getUniqueColor(i) }" v-for="(user, i) in trip.participants">{{
                        user.name
                    }}</span>
                </div>
            </div>
        </template>
    </Layout>
</template>

<style scoped>
span.tag {
    background-color: #FF4136;
    display: inline-block;
    text-align: center;
    padding: 0.3em;
    font-size: 0.8em;
    border-radius: 50%;
    color: #fff;
    /* padding: 0.5em; */
}


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