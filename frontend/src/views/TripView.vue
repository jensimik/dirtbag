<script setup>
import TripMethodsAPI from '../api/resources/TripMethods';
import WeatherMethodsAPI from '../api/resources/WeatherMethods';
import { ref } from 'vue';

import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, LineElement, CategoryScale, TimeScale, LinearScale, PointElement } from 'chart.js'
import 'chartjs-adapter-luxon';

ChartJS.register(Title, Tooltip, Legend, BarElement, LineElement, PointElement, CategoryScale, TimeScale, LinearScale)
const chartOptions = {
    plugins: {
        legend: {
            display: false,
        }
    },
    scales: {
        x: {
            type: 'time',
            time: {
                unit: 'hour',
                displayFormats: {
                    hour: 'HH:mm'
                },
            },
            title: {
                display: false,
                text: 'Date'
            },
            ticks: {
                major: {
                    enabled: true,
                },
                // autoSkip: false,
                maxRotation: 0,
            }
        },
        y: {
            title: {
                display: false,
                text: 'temperature C'
            }
        },
        yPrecipitation: {
            title: {
                display: false,
                text: 'precipitation mm'
            },
            position: 'right',
        }
    },
    responsive: true
}

const props = defineProps(['id'])

const trip = ref({});
const participants = ref({});
const trip_data = await TripMethodsAPI.get(props.id);
trip_data.participants.forEach(participant => {
    participants.value[participant.user_id] = participant;
});
trip.value = trip_data;

const chartData = ref({});
const weatherData = await WeatherMethodsAPI.get(trip.value.sectors[0].name);
chartData.value = {
    "labels": weatherData.x,
    "datasets": [
        {
            type: "line",
            label: "temperature",
            data: weatherData.temperature,
            borderColor: "red",
        },
        {
            type: "bar",
            label: "precipitation",
            data: weatherData.precipitation,
            // borderColor: "blue",
            backgroundColor: 'blue',
            yAxisID: "yPrecipitation"
        }
    ]

}
</script>

<template>
    <div>
        <h2>{{ trip.area_name }}</h2>

        <div class="flex one">
            <div class="flex grow">
                <div v-for="user in trip.participants" :key="user.user_id"><router-link
                        :to="{ name: 'user', params: { id: user.id } }"><img class="thumb" :src="user.thumb_url" />
                        {{ user.name }}</router-link></div>
            </div>
        </div>
        <Bar id="my-chart-id" :options="chartOptions" :data="chartData" />
        <div v-for="sector in trip.sectors" :key="sector.app_url">
            <h3><a :href="$isMobile() ? sector.app_url : sector.url">{{
                sector.name
            }}</a><a
                    :href="'https://maps.google.com/?q=@' + sector.location[0] + ',' + sector.location[1] + ',10z'">📍</a>
            </h3>
            <div class="flex three" v-for="todo in sector.todos">
                <div class="four-fifth"><a :href="$isMobile() ? todo.app_url : todo.url"><img class="thumb"
                            :src="todo.thumb_url" />
                        {{ todo.grade }} {{ todo.name }}</a></div>
                <div class="fifth right">
                    <router-link :to="{ name: 'user', params: { id: participants[user_id].id } }"
                        v-for="user_id in todo.user_ids" :key="user_id"><img class="thumb"
                            :src="participants[user_id].thumb_url" :title="participants[user_id].name" /></router-link>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
img.thumb {
    height: 1.5em;
    width: 1.5em;
}

img.header {
    width: 100%;
}

div.right {
    text-align: right;
}
</style>