import { APISettings } from '../config.js';

export default {

    async index() {
        const response = await fetch(APISettings.baseURL + '/users', {
            method: 'GET',
            headers: APISettings.headers
        });
        if (response.status != 200) {
            throw response.status;
        } else {
            return response.json();
        }
    },
    async get(user_id) {
        const response = await fetch(APISettings.baseURL + '/users/' + user_id, {
            method: 'GET',
            headers: APISettings.headers
        });
        if (response.status != 200) {
            throw response.status;
        } else {
            return response.json();
        }
    },
    async get_areas(user_id) {
        const response = await fetch(APISettings.baseURL + '/users/' + user_id + '/areas', {
            method: 'GET',
            headers: APISettings.headers
        });
        if (response.status != 200) {
            throw response.status;
        } else {
            return response.json();
        }
    },
    async get_todos(user_id, area_name) {
        const response = await fetch(APISettings.baseURL + '/users/' + user_id + '/area/' + area_name + '/todos', {
            method: 'GET',
            headers: APISettings.headers
        });
        if (response.status != 200) {
            throw response.status;
        } else {
            return response.json();
        }
    },
}