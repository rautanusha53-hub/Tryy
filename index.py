const API_URL = "/api/player";

async function lookupPlayer(uid) {
    const url = new URL(API_URL, window.location.origin);
    url.searchParams.set("uid", uid);
    url.searchParams.set("key", "HNTH");

    const response = await fetch(url.toString());
    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.message || data.error || "Player lookup failed"
        );
    }

    return data;
}
