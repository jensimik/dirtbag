import { APISettings } from '../config.js';

export default {

    async index() {
        const response = await fetch(APISettings.baseURL + '/trips', {
            method: 'GET',
            headers: APISettings.headers
        });
        if (response.status != 200) {
            throw response.status;
        } else {
            return response.json();
        }
    },
    async get(trip_id) {
        const response = await fetch(APISettings.baseURL + '/trips/' + trip_id, {
            method: 'GET',
            headers: APISettings.headers
        });
        if (response.status != 200) {
            throw response.status;
        } else {
            return response.json();
        }
    },
    async get(trip_id, pin) {
        const response = await fetch(APISettings.baseURL + '/trips/' + trip_id + '/' + pin, {
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