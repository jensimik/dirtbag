import { createApp } from 'vue';
import App from './App.vue';
import VueMobileDetection from "vue-mobile-detection";
import router from './router'

const app = createApp(App);

app.use(VueMobileDetection);
app.use(router)
app.mount('#app')
