<script setup>
import Layout from '../components/Layout.vue';
import UserMethodsAPI from '../api/resources/UserMethods';
import { ref } from 'vue';

const props = defineProps(['id'])
const areas = ref([]);

areas.value = await UserMethodsAPI.get_areas(props.id);
</script>

<template>
    <Layout>
        <template v-slot:title>{{ props.id }}</template>
        <template v-slot:content>
            <h3>Todos</h3>
            <div v-for="area in areas">
                <div><router-link :to="{ name: 'user_area_view', params: { user_id: props.id, area_name: area.name } }">{{
                    area.name
                }}</router-link> ({{ area.todos_count }})</div>
            </div>
        </template>
    </Layout>
</template>

<style scoped>
img.thumb {
    width: 1.5em;
    height: 1.5em;
}
</style>