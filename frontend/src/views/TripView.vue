<script setup>
import TripMethodsAPI from '../api/resources/TripMethods';
import WeatherMethodsAPI from '../api/resources/WeatherMethods';
import { ref } from 'vue';

import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, LineController, LineElement, CategoryScale, TimeScale, LinearScale, PointElement } from 'chart.js'
import 'chartjs-adapter-luxon';

ChartJS.register(Title, Tooltip, Legend, BarElement, LineController, LineElement, PointElement, CategoryScale, TimeScale, LinearScale)
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
        <div class="met_license">
            <a href="https://www.met.no/en/free-meteorological-data/Licensing-and-crediting">forecast based on data from
                MET
                Norway</a>
        </div>
        <div v-for="sector in trip.sectors" :key="sector.app_url">
            <h3><a :href="$isMobile() ? sector.app_url : sector.url">{{
                sector.name
            }}</a><a
                    :href="'https://maps.google.com/?q=@' + sector.location[0] + ',' + sector.location[1] + ',10z'">📍</a>
            </h3>
            <div v-for="todo in sector.todos">
                <div class="flex three">
                    <div class="four-fifth"><a :href="$isMobile() ? todo.app_url : todo.url"><img class="thumb"
                                :src="todo.thumb_url" />
                            {{ todo.grade }} {{ todo.name }}</a></div>
                    <div class="fifth right">
                        <router-link :to="{ name: 'user', params: { id: participants[user_id].id } }"
                            v-for="user_id in todo.user_ids" :key="user_id"><img class="thumb"
                                :src="participants[user_id].thumb_url"
                                :title="participants[user_id].name" /></router-link>
                    </div>
                </div>
                <div v-if="todo.comment">
                    <div>{{ todo.comment }}</div>
                </div>
                <div class="flex one" v-if="todo.name == 'Symbiose'">
                    <div class="off-abit">
                        <a href="https://bettybeta.com/bouldering/fontainebleau/95-2-ouest/symbiose">
                            <svg class="youtube" viewBox="0 0 159 110" width="159" height="110"
                                xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="m154 17.5c-1.82-6.73-7.07-12-13.8-13.8-9.04-3.49-96.6-5.2-122 0.1-6.73 1.82-12 7.07-13.8 13.8-4.08 17.9-4.39 56.6 0.1 74.9 1.82 6.73 7.07 12 13.8 13.8 17.9 4.12 103 4.7 122 0 6.73-1.82 12-7.07 13.8-13.8 4.35-19.5 4.66-55.8-0.1-75z"
                                    fill="#f00" />
                                <path d="m105 55-40.8-23.4v46.8z" fill="#fff" />
                            </svg>
                            betty beta
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>

</template>

<style scoped>
.off-abit {
    margin-left: 2em;
}

svg.youtube {
    height: 1em;
    width: auto;
}

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

div.met_license {
    text-align: right;
    font-size: 0.5em;
}
</style>