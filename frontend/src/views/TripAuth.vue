<script setup>
import { ref } from 'vue';
import TripMethods from '../api/resources/TripMethods';
import router from '../router';

const props = defineProps(['id'])

const trip = ref({});
const auth_code = ref("");

trip.value = await TripMethods.get_no_auth(props.id);

const auth = async () => {
    router.push({ name: 'trip_auth', params: { pin: auth_code.value } });
    return false;
}

</script>

<template>
    <h2>{{ trip.area_name }}</h2>
    <label for="password">Enter code</label>
    <input id="password" type="password" v-model="auth_code" />
    <button class="button" @click="auth">auth</button>
</template>