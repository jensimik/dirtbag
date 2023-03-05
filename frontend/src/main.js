import { createApp } from 'vue';
import App from './App.vue';
import VueMobileDetection from "vue-mobile-detection";
//import OpenLayersMap from 'vue3-openlayers';
//import 'vue3-openlayers/dist/vue3-openlayers.css';
import router from './router';
import "../node_modules/picnic/picnic.min.css";

const app = createApp(App);

app.use(VueMobileDetection);
//app.use(OpenLayersMap)
app.use(router)
app.mount('#app')
