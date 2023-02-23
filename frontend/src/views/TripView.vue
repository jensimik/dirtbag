<script setup>
import TripMethodsAPI from '../api/resources/TripMethods';
//import WeatherMethodsAPI from '../api/resources/WeatherMethods';
import { ref } from 'vue';
import router from '../router';
//import { boundingExtent, getCenter, buffer } from 'ol/extent';


//import { Bar } from 'vue-chartjs'
//import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, LineController, LineElement, CategoryScale, TimeScale, LinearScale, PointElement } from 'chart.js'
//import 'chartjs-adapter-luxon';

//ChartJS.register(Title, Tooltip, Legend, BarElement, LineController, LineElement, PointElement, CategoryScale, TimeScale, LinearScale)
//const chartOptions = {
//    plugins: {
//        legend: {
//            display: false,
//        }
//    },
//    scales: {
//        x: {
//            type: 'time',
//            time: {
//                unit: 'hour',
//                displayFormats: {
//                    hour: 'HH:mm'
//                },
//            },
//            title: {
//                display: false,
//                text: 'Date'
//            },
//            ticks: {
//                major: {
//                    enabled: true,
//                },
//                // autoSkip: false,
//                maxRotation: 0,
//            }
//        },
//        y: {
//            title: {
//                display: false,
//                text: 'temperature C'
//            }
//        },
//        yPrecipitation: {
//            title: {
//                display: false,
//                text: 'precipitation mm'
//            },
//            position: 'right',
//        }
//    },
//    responsive: true
//}

const props = defineProps(['id', 'pin']);

const trip = ref({});
const participants = ref({});
const loading = ref(true);
const error = ref(false);
//const chartData = ref({});
const getUniqueColor = (n) => {
    const rgb = [0, 0, 0];

    for (let i = 0; i < 24; i++) {
        rgb[i % 3] <<= 1;
        rgb[i % 3] |= n & 0x01;
        n >>= 1;
    }
    return '#' + rgb.reduce((a, c) => (c > 0x0f ? c.toString(16) : '0' + c.toString(16)) + a, '')
}
try {
    const trip_data = await TripMethodsAPI.get(props.id, props.pin);
    trip_data.participants.forEach((participant, i) => {
        participant.background_color = getUniqueColor(i);
        participants.value[participant.user_id] = participant;
    });
    trip.value = trip_data;
//    const weatherData = await WeatherMethodsAPI.get(trip.value.sectors[0].name);
//    chartData.value = {
//        "labels": weatherData.x,
//        "datasets": [
//            {
//                type: "line",
//                label: "temperature",
//                data: weatherData.temperature,
//                borderColor: "red",
//            },
//            {
//                type: "bar",
//                label: "precipitation",
//                data: weatherData.precipitation,
//                // borderColor: "blue",
//                backgroundColor: 'blue',
//                yAxisID: "yPrecipitation"
//            }
//        ]
//    }
    loading.value = false;
} catch (e) {
    console.log(e);
    error.value = "failed to auth";
    router.push({ name: 'auth_trip', params: { id: props.id } });
}

// map settings
//const locations = trip.value.sectors.map(sector => [sector.location[1], sector.location[0]]);
//const map_extent = buffer(boundingExtent(locations), 0.05);
//const center = ref(getCenter(map_extent));
//const projection = ref("EPSG:4326");
//const zoom = ref(10);
//const rotation = ref(0);

//const zoomChanged = async (currentZoom) => {
//    zoom.value = currentZoom;
//}

//const view = ref(null);
//const geoLocChange = (loc) => {
//    console.log(loc);
    // view.value.fit([loc[0], loc[1], loc[0], loc[1]], {
    //     maxZoom: 14
    // })
//}
//const getRndInteger = (min, max) => {
//    return Math.floor(Math.random() * (max - min)) + min;
//}
</script>

<template>
    <div v-if="!loading">
        <div class="flex two">
            <h2>{{ trip.area_name }}</h2>
            <div class="right"><router-link :to="{ name: 'trip_edit', params: { id: props.id, pin: props.pin } }"
                    class="button right">edit</router-link></div>
        </div>
<!--         <div v-if="false">
            <Bar id="my-chart-id" :options="chartOptions" :data="chartData" />
            <div class="met_license">
                <a href="https://www.met.no/en/free-meteorological-data/Licensing-and-crediting">forecast based on data
                    from
                    MET
                    Norway</a>
            </div>
        </div>
 --><!--         <div>
            <ol-map style="height:400px">
                <ol-view ref="view" :center="center" :extent="map_extent" :projection="projection" />

                <ol-attribution-control />
                <ol-scaleline-control />
                <ol-zoom-control />
                <ol-zoomtoextent-control :extent="map_extent" tipLabel="Fit to Area" />
                <ol-tile-layer>
                    <ol-source-osm />
                </ol-tile-layer>
                <ol-overlay :stopEvent="false" :position="[sector.location[1], sector.location[0]]"
                    v-for="(sector, i) in trip.sectors">
                    <template v-slot="slotProps" id="test">
                        <div class="marker" :style="{ transform: 'rotate(' + getRndInteger(-90, 90) + 'deg)' }">
                            📍 {{ sector.name }}</div>
                    </template>
                </ol-overlay>
                <ol-geolocation :projection="projection" @positionChanged="geoLocChange">
                        <template v-slot="slotProps">
                            <ol-vector-layer :zIndex="2">
                                <ol-source-vector>
                                    <ol-feature ref="positionFeature">
                                        <ol-geom-point :coordinates="slotProps.position"></ol-geom-point>
                                        <ol-style>
                                            <ol-style-icon src="https://dirtbag.gnerd.dk/apple-touch-icon.png"
                                                :scale="0.25"></ol-style-icon>
                                        </ol-style>
                                    </ol-feature>
                                </ol-source-vector>
                            </ol-vector-layer>
                        </template>
                    </ol-geolocation>
            </ol-map>
        </div> -->
        <div v-for="sector in trip.sectors" :key="sector.app_url">
            <h3><a :href="$isMobile() ? sector.app_url : sector.url">{{
                sector.name
            }}</a><a
                    :href="'https://maps.google.com/?q=@' + sector.location[0] + ',' + sector.location[1] + ',10z'">📍</a>
            </h3>
            <div v-for="todo in sector.todos">
                <div class="flex grow todo_line">
                    <div class="thumb">
                        <img class="thumb" :src="todo.thumb_url" @click="e => e.target.classList.toggle('expand')" />
                    </div>
                    <div class="todo_title">
                        <a :href="$isMobile() ? todo.app_url : todo.url">{{ todo.grade }} {{
                            todo.name
                        }}</a>
                    </div>
                    <div class="participants">
                        <span class="tag" :style="{
                            backgroundColor: participants[user_id].background_color,
                            color: participants[user_id].color
                        }" v-for="user_id in todo.user_ids">{{
    participants[user_id].name
}}</span>
                    </div>
                </div>
                <div class="flex grow comment_line" v-if="todo.comments.length > 0">
                    <div class="thumb"></div>
                    <div class="comment"><span class="comment" v-for="comment in todo.comments"><a :href="comment.url"
                                v-if="comment.type == 'link'">
                                <svg v-if="comment.url.includes('youtube') || comment.url.includes('youtu.be')"
                                    class="youtube" viewBox="0 0 159 110" width="159" height="110"
                                    xmlns="http://www.w3.org/2000/svg">
                                    <path
                                        d="m154 17.5c-1.82-6.73-7.07-12-13.8-13.8-9.04-3.49-96.6-5.2-122 0.1-6.73 1.82-12 7.07-13.8 13.8-4.08 17.9-4.39 56.6 0.1 74.9 1.82 6.73 7.07 12 13.8 13.8 17.9 4.12 103 4.7 122 0 6.73-1.82 12-7.07 13.8-13.8 4.35-19.5 4.66-55.8-0.1-75z"
                                        fill="#f00" />
                                    <path d="m105 55-40.8-23.4v46.8z" fill="#fff" />
                                </svg>
                                <span v-else>{{ comment.text }}</span>
                            </a>
                            <span v-else>{{ comment.text }}</span>
                            &MediumSpace;</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div v-if="error">
        {{ error }}
</div>
</template>

<style scoped>
.marker {
    font-size: 0.6em;
    transform-origin: top left;
    z-index: -2;
}

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

.right {
    text-align: right;
}

div.todo_line {
    justify-content: stretch;
    margin-bottom: -0.4em;
    margin-top: -0.4em;
}

div.comment_line {
    margin-top: -1.5em;
    justify-content: stretch;
    margin-bottom: -0.5em;
}

div.thumb {
    flex-basis: 2em;
    flex-grow: 0;
}

img.expand {
    width: 6em !important;
    height: 6em !important;

}

div.comment {
    width: auto;
    flex-grow: 1;
}

div.comment span.comment {
    font-size: 0.6em;
}

div.todo_title {
    flex-basis: calc(100% - 8em);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

div.participants {
    flex-basis: 4em;
    text-align: right;
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


div.met_license {
    text-align: right;
    font-size: 0.5em;
}
</style>