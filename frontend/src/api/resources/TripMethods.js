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
    async get_no_auth(trip_id) {
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
    async update(trip_id, pin, participants) {
        const response = await fetch(APISettings.baseURL + '/trips/' + trip_id + '/' + pin + '/update', {
            method: 'POST',
            headers: { ...APISettings.headers, 'Content-Type': 'Application/json' },
            body: JSON.stringify(participants)
        });
        if (response.status != 200) {
            throw response.status;
        } else {
            return response.json();
        }
    },
    async create(new_trip) {
        const response = await fetch(APISettings.baseURL + '/trips', {
            method: 'POST',
            headers: { ...APISettings.headers, 'Content-Type': 'Application/json' },
            body: JSON.stringify(new_trip)
        });
        if (response.status != 200) {
            throw response.status;
        } else {
            return response.json();
        }
    },
    async resync(trip_id, pin) {
        const response = await fetch(APISettings.baseURL + '/trips/' + trip_id + '/' + pin + '/resync', {
            method: 'POST',
            headers: APISettings.headers
        });
        if (response.status != 200) {
            throw response.status;
        } else {
            return response.json();
        }
    },
}