<script setup>
import { ref } from 'vue';
import TripMethods from '../api/resources/TripMethods';

const props = defineProps(['id'])

const trip = ref({});

trip.value = await TripMethods.get(props.id);
</script>

<template>
    <h2>{{ trip.area_name }}</h2>
    <label for="password">Enter code</label>
    <input id="password" type="password" />
    <button class="button">auth</button>
</template>

<style scoped>

</style>