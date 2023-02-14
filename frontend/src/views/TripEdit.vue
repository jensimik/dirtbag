<script setup>
import TripMethodsAPI from '../api/resources/TripMethods';
import { ref } from 'vue';
import router from '../router';


const resyncing = ref(false);
const resync = async () => {
    resyncing.value = true;
    await TripMethodsAPI.resync(props.id, props.pin);
    await new Promise(r => setTimeout(r, 10000));
    resyncing.value = false;
}
</script>

<template>
    <button class="button action" :disabled="resyncing" @click="resync">resync 27crags</button>
</template>