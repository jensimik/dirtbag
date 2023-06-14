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
        <template v-slot:title>dirtbag
        </template>
        <template v-slot:menu>
            <router-link :to="{ name: 'trip_add' }" class="button">create</router-link>
        </template>
        <template v-slot:content>
            <h2>Current/Upcoming</h2>
            <div class="flex three" v-for=" trip in trips.current" :key="trip.id">
                <div><router-link :to="{ name: 'trip_view', params: { id: trip.id } }">{{ trip.area_name }}</router-link></div>
                <div v-if="$isMobile()">{{ trip.date_from_display.replace(/\s+/g, '').toLowerCase() }}+{{ trip.duration }}d</div>
                <div v-else>
                    {{ trip.date_from_display }} -{{ trip.date_to_display }} ({{
                    trip.duration ? trip.duration + ' days' :
                        'daytrip'
                }})
                </div>
                <div class="right">
                    <span class="tag" :style="{ backgroundColor: getUniqueColor(i) }" v-for="(user, i) in trip.participants.slice(0,5)">{{
                        user.name
                    }}</span>
                    <span v-if="trip.participants.length > 5" class="tag">+{{ trip.participants.length - 5 }}</span>
                </div>
            </div>
            <h2>History</h2>
            <div class="flex three" v-for=" trip in trips.past" :key="trip.id">
                <div><router-link :to="{ name: 'trip_view', params: { id: trip.id } }">{{ trip.area_name }}</router-link></div>
                <div v-if="$isMobile()">{{ trip.date_from_display.replace(/\s+/g, '').toLowerCase() }}+{{ trip.duration }}d</div>
                <div v-else>
                    {{ trip.date_from_display }} -{{ trip.date_to_display }} ({{
                    trip.duration ? trip.duration + ' days' :
                        'daytrip'
                }})                    
                </div>
                <div class="right">
                    <span class="tag" :style="{ backgroundColor: getUniqueColor(i) }" v-for="(user, i) in trip.participants.slice(0,5)">{{
                        user.name
                    }}</span>
                    <span v-if="trip.participants.length > 5" class="tag">+{{ trip.participants.length - 5 }}</span>
                </div>
            </div>
            <p>this is an effort to make the 27crags todo lists more useful. see a combined todo-list for a group of ppl, ordered by sectors and grades (and see who in the group already sent your projects?). bugs/info/etc contact jens@dirtbag.dk</p>
            <p>idea: "live" mode when at the crag see the todo-list live-updated with nearest boulders (require premium data though)</p>
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
    /* overlap a bit */
    margin-left: -0.5em;
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
@media only screen and (max-width: 600px) {
    span.tag {
        margin-left: -0.8em;
    }
}
</style>