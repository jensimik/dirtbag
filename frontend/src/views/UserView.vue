<script setup>
import UserMethodsAPI from '../api/resources/UserMethods';
import { ref } from 'vue';

const props = defineProps(['id'])
const user = ref({});
const areas = ref([]);

user.value = await UserMethodsAPI.get(props.id);
areas.value = await UserMethodsAPI.get_areas(props.id);
</script>

<template>
    <h2><img class="thumb" :src="user.thumb_url" /> {{ user.name }}</h2>


    <h3>Todos</h3>
    <div v-for="area in areas">
        <div><router-link :to="{ name: 'user_area_view', params: { user_id: props.id, area_name: area.name } }">{{
            area.name
        }}</router-link> ({{ area.todos_count }})</div>
    </div>
</template>

<style scoped>
img.thumb {
    width: 1.5em;
    height: 1.5em;
}
</style>