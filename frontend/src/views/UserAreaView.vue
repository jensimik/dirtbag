<script setup>
import UserMethodsAPI from '../api/resources/UserMethods';
import { ref } from 'vue';

const props = defineProps(['id', 'area_name'])
const user = ref({});
const sectors = ref([]);

user.value = await UserMethodsAPI.get(props.id);
sectors.value = await UserMethodsAPI.get_todos(props.id, props.area_name);
</script>

<template>
    <h2><img class="thumb" :src="user.thumb_url" /> {{ user.name }}</h2>


    <h3>{{ area_name }}</h3>
    <div v-for="sector in sectors">
        <h3><a :href="$isMobile() ? sector.app_url : sector.url">{{
            sector.name
        }}</a><a
                :href="'https://maps.google.com/?q=@' + sector.location[0] + ',' + sector.location[1] + ',10z'">📍</a>
        </h3>
        <div class="flex one" v-for="todo in sector.todos">
            <div><a :href="$isMobile() ? todo.app_url : todo.url"><img class="thumb" :src="todo.thumb_url" />
                    {{ todo.grade }} {{ todo.name }}</a></div>
        </div>
    </div>
</template>

<style scoped>
img.thumb {
    width: 1.5em;
    height: 1.5em;
}
</style>