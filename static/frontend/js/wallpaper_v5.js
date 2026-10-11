let jadwal_sholat;
let analogclock, secondshand, minuteshand, hourshand, soundtoggle, context;
let digitalclock, digitalclock_imsak, digitalclock_shubuh, digitalclock_dzuhur, digitalclock_ashar, digitalclock_maghrib, digitalclock_isya;
let imsak, subuh, dzuhur, ashar, maghrib, isya, iqamah;
let iqamah_state;
let iqamah_time = 1;

let current_date;

let now, h, m, s, timerid;
let ticking = false;
let timer = false;

document.addEventListener('DOMContentLoaded', function (e) {
    try { synchJadwalSholat(); loadSlide();} catch (error) {
        console.log("Data didn't load", error);
    }
});

/* ================= TAMBAHAN ================= */
let adzanAudio;
let iqamahInterval = null;

document.addEventListener('DOMContentLoaded', function () {
    document.documentElement.style.colorScheme = "light";
    document.body.style.backgroundColor = "#ffffff";
    adzanAudio = document.getElementById("adzan-audio");

    try { synchJadwalSholat(); loadSlide();} catch (error) {
        console.log("Data didn't load", error);
    }
});

document.addEventListener('click', function () {
    try {
        adzanAudio.play().then(() => {
            adzanAudio.pause();
            adzanAudio.currentTime = 0;
            console.log("Audio unlocked");
        }).catch(() => {});
    } catch (e) {}
}, { once: true });

/* ================= AUDIO ================= */

let isAdzanPlaying = false;

function playAdzan() {
    try {
        console.log("PLAY ADZAN DIPANGGIL");

        adzanAudio.pause();
        adzanAudio.currentTime = 0;
        adzanAudio.muted = false;
        adzanAudio.volume = 1;

        adzanAudio.play().then(() => {
            console.log("AUDIO BUNYI ✅");
        }).catch((e) => {
            console.log("GAGAL PLAY ❌", e);
        });

    } catch (e) {
        console.log("ERROR:", e);
    }
}

/* ================= IQAMAH FULLSCREEN ================= */

function showIqamahBanner(waktuSholat, jenisSholat) {

    let banner = $('#iqamah-banner');
    banner.fadeIn();

    $('.owl-carousel').trigger('stop.owl.autoplay');

    iqamah = new Date();

    let tambahanMenit = parseInt(IQAMAH_TIME[jenisSholat.toLowerCase()] || 7);
    iqamah.setMinutes(iqamah.getMinutes() + tambahanMenit);

    let timerEl = $('#iqamah-timer');

    iqamahInterval = setInterval(function () {

        let nowLocal = new Date();
        let diff = (iqamah - nowLocal) / 1000;

        if (diff <= 0) {
    clearInterval(iqamahInterval);

    // 🔥 stop dulu timer
    timer = false;

    // 🔥 reset & play adzan
    adzanAudio.pause();
    adzanAudio.currentTime = 0;

    adzanAudio.onended = function () {
        // ✅ setelah audio selesai baru lanjut
        banner.fadeOut();
        $('.owl-carousel').trigger('play.owl.autoplay');

        // cleanup biar tidak nembak berkali-kali
        adzanAudio.onended = null;
    };

    adzanAudio.play().catch(e => {
        console.log("Gagal play:", e);

        // fallback kalau gagal play → tetap lanjut
        banner.fadeOut();
        $('.owl-carousel').trigger('play.owl.autoplay');
    });

    return;
    }

            timerEl.text(get_elapsed_time_string(diff));

        }, 1000);
    }


function setDefaultTimeColor() {
    // Reset semua warna ke default
    $('.shalat-text .shalat, .shalat-text .shalat-time, .shalat-icon').css({ "color": "color" });

    let activeShalatId = null;

    if (now >= isya) {
        activeShalatId = 'digitalclock_isya';
        iqamah_state = 'Isya';
    } else if (now >= maghrib) {
        activeShalatId = 'digitalclock_maghrib';
        iqamah_state = 'Maghrib';
    } else if (now >= ashar) {
        activeShalatId = 'digitalclock_ashar';
        iqamah_state = 'Ashar';
    } else if (now >= dzuhur) {
        activeShalatId = 'digitalclock_dzuhur';
        iqamah_state = 'Dzuhur';
    } else if (now >= subuh) {
        activeShalatId = 'digitalclock_shubuh';
        iqamah_state = 'Subuh';
    } else if (now >= imsak) {
        activeShalatId = 'digitalclock_imsak';
        iqamah_state = 'Imsak';
    }

    if (activeShalatId) {
        // Naik ke .col lalu cari semua elemen yang perlu diwarnai
        let activeCol = $('#' + activeShalatId).closest('.col');
        activeCol.find('.shalat, .shalat-time, .shalat-icon').css({ "color": "#FFFF81" });
    }
}

function synchJadwalSholat() {
    $.ajax({
        type: "POST",
        url: '/ajax/synch_jadwal_sholat/',
        datatype: 'json',
        success: function (data) {
            jadwal_sholat = JSON.parse(data.jadwal_sholat);
            setPrayTime();
            init();
            current_date = new Date();
        }
    });
}

function setPrayTime() {

    now = new Date();

    imsak = new Date();
    imsak.setHours(jadwal_sholat['imsak'].split(':')[0], jadwal_sholat['imsak'].split(':')[1], 0);

    subuh = new Date();
    subuh.setHours(jadwal_sholat['subuh'].split(':')[0], jadwal_sholat['subuh'].split(':')[1], 0);

    dzuhur = new Date();
    dzuhur.setHours(jadwal_sholat['dzuhur'].split(':')[0], jadwal_sholat['dzuhur'].split(':')[1], 0);
    

    ashar = new Date();
    ashar.setHours(jadwal_sholat['ashar'].split(':')[0], jadwal_sholat['ashar'].split(':')[1], 0);

    maghrib = new Date();
    maghrib.setHours(jadwal_sholat['maghrib'].split(':')[0], jadwal_sholat['maghrib'].split(':')[1], 0);

    isya = new Date();
    isya.setHours(jadwal_sholat['isya'].split(':')[0], jadwal_sholat['isya'].split(':')[1], 0);

    iqamah = new Date();
    now = new Date();

    setDefaultTimeColor();
}

function init() {

    secondshand = gid("secondshand");
    minuteshand = gid("minuteshand");
    hourshand = gid("hourshand");
    analogclock = gid("analogclock");

    digitalclock = gid("digitalclock");
    digitalclock_imsak = gid("digitalclock_imsak");
    digitalclock_shubuh = gid("digitalclock_shubuh");
    digitalclock_dzuhur = gid("digitalclock_dzuhur");
    digitalclock_ashar = gid("digitalclock_ashar");
    digitalclock_maghrib = gid("digitalclock_maghrib");
    digitalclock_isya = gid("digitalclock_isya");

    digitalclock_imsak.innerHTML = imsak.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit' }).replace(':', ' : ');
    digitalclock_shubuh.innerHTML = subuh.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit' }).replace(':', ' : ');
    digitalclock_dzuhur.innerHTML = dzuhur.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit' }).replace(':', ' : ');
    digitalclock_ashar.innerHTML = ashar.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit' }).replace(':', ' : ');
    digitalclock_maghrib.innerHTML = maghrib.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit' }).replace(':', ' : ');
    digitalclock_isya.innerHTML = isya.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit' }).replace(':', ' : ');

    soundtoggle = gid("soundtoggle");
    makeMinMarkers();
    makeClockNumbers();
    timerid = setInterval(update, 1000);
}

function getNextPrayTime() {
    let prayers = [
        { name: 'Subuh', time: subuh },
        { name: 'Dzuhur', time: dzuhur },
        { name: 'Ashar', time: ashar },
        { name: 'Maghrib', time: maghrib },
        { name: 'Isya', time: isya },
    ];

    // cari waktu sholat berikutnya yang lebih besar dari sekarang
    for (let i = 0; i < prayers.length; i++) {
        if (now < prayers[i].time) {
            return prayers[i];
        }
    }

    // jika semua sudah lewat, kembalikan subuh hari berikutnya
    let nextSubuh = new Date(subuh);
    nextSubuh.setDate(nextSubuh.getDate() + 1);
    return { name: 'Subuh', time: nextSubuh };
}

function updateCountdown() {
    let next = getNextPrayTime();
    let diff = (next.time - now) / 1000; // selisih dalam detik

    $('#countdown-shalat').text(next.name);
    $('#countdown-time').text("-" + get_elapsed_time_string(diff));
}

function updateAudioProgress(oEvent) {
    if (oEvent.lengthComputable) {
        let pc = oEvent.loaded / oEvent.total;
        if (pc >= 1) { }
    }
}

function tickLoadChecker(audioObject) {
    console.log("tick audio loaded from " + audioObject.url);
}

function update() {
    now = new Date();

    if (now.getDate() !== current_date.getDate()) {
        clearInterval(timerid);
        synchJadwalSholat();
    }

    let oldsecond = s;
    h = now.getHours();
    m = now.getMinutes();
    s = now.getSeconds();
    secondshand.style.transform = `rotate(${s * 6}deg)`;
    minuteshand.style.transform = `rotate(${m * 6}deg)`;
    hourshand.style.transform = `rotate(${(h * 30) + ((m / 60) * 30)}deg)`;

    digitalclock.innerHTML = now.toLocaleTimeString([], { hour12: false });

    setDefaultTimeColor();
    updateCountdown();

    if (!timer) checkIqamah();
}

function formatTime(time) {
    return time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }).replace(':', ' : ');
}

function checkIqamah() {

    function trigger(waktu, jenis) {
        timer = true;

        // reset audio
        adzanAudio.pause();
        adzanAudio.currentTime = 0;

        // 🔥 setelah adzan selesai → tampil iqamah
        adzanAudio.onended = function () {
            showIqamahBanner(waktu, jenis);

            // cleanup biar tidak ke-trigger lagi
            adzanAudio.onended = null;
        };

        // play adzan
        adzanAudio.play().catch(e => {
            console.log("Gagal play:", e);

            // fallback kalau gagal → tetap lanjut iqamah
            showIqamahBanner(waktu, jenis);
        });
    }

    if (now.getHours() === subuh.getHours() && now.getMinutes() === subuh.getMinutes()) {
        trigger(subuh, 'subuh');
    } 
    else if (now.getHours() === dzuhur.getHours() && now.getMinutes() === dzuhur.getMinutes()) {
        trigger(dzuhur, 'dzuhur');
    } 
    else if (now.getHours() === ashar.getHours() && now.getMinutes() === ashar.getMinutes()) {
        trigger(ashar, 'ashar');
    } 
    else if (now.getHours() === maghrib.getHours() && now.getMinutes() === maghrib.getMinutes()) {
        trigger(maghrib, 'maghrib');
    } 
    else if (now.getHours() === isya.getHours() && now.getMinutes() === isya.getMinutes()) {
        trigger(isya, 'isya');
    }
}

function gid(idstring) {
    return document.getElementById(idstring);
}

function makeMinMarkers() {
    let minmarkers = gid("minmarkers");
    let code = "";
    for (let i = 0; i < 30; i++) {
        let classname = i % 5 === 0 ? "guide" : "guidedot";
        let angle = i * 6;
        code += `<div class="${classname}" style="--angle:${angle}deg;"></div>`;
    }
    minmarkers.innerHTML = code;
}

function makeClockNumbers() {
    let clocknumbers = gid("clocknumbers");
    let clocknumbers24 = gid("clocknumbers24");
    let nums = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2];
    let code = "";
    for (let i = 0; i < 12; i++) {
        code += `<div class="clockdigits">${nums[i]}</div>`;
    }
    clocknumbers.innerHTML = code;

    let cns = document.querySelectorAll(".clockdigits");
    for (let i = 0; i < 12; i++) {
        let p = getCirclePoint(50, (i * 30), 50, 50);
        cns[i].style.left = `calc(${p.x}% - 2em)`;
        cns[i].style.top = `calc(${p.y}% - 0.75em)`;
    }
}

function getCirclePoint(r, degrees, cx, cy) {
    let angleInRadians = degrees * (Math.PI / 180);
    let x = cx + r * Math.cos(angleInRadians);
    let y = cy + r * Math.sin(angleInRadians);
    return { x, y };
}

function get_elapsed_time_string(total_seconds) {
    function pretty_time_string(num) {
        return (num < 10 ? "0" : "") + num;
    }

    var hours = Math.floor(total_seconds / 3600);
    total_seconds = total_seconds % 3600;

    var minutes = Math.floor(total_seconds / 60);
    total_seconds = total_seconds % 60;

    var seconds = Math.floor(total_seconds);

    hours = pretty_time_string(hours);
    minutes = pretty_time_string(minutes);
    seconds = pretty_time_string(seconds);

    var currentTimeString = hours + ":" + minutes + ":" + seconds;

    return currentTimeString;
}

function getAudio(audioObject, callback) {
    context = new (window.AudioContext || window.webkitAudioContext)();
    let req = new XMLHttpRequest();
    req.audioObject = audioObject;
    req.open("GET", audioObject.url, true);
    req.responseType = "arraybuffer";
    req.addEventListener("progress", updateAudioProgress, false);
    req.onload = function () {
        context.decodeAudioData(req.response, function (buffer) {
            audioObject.buffer = buffer;
            if (callback) {
                callback(audioObject);
            }
        });
    };
    req.send();
}

function playTick(audioBuffer) {
    if (context.state === "suspended") {
        context.resume();
    }
    let source = context.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(context.destination);
    source.start();
}


let currentType = "hadith";

function loadSlide() {
    fetch("/ajax/get_random_slide/")
    .then(res => res.json())
    .then(data => {

        if (!data || data.type === "error") {
            console.log("ERROR:", data);
            return;
        }

        var box = document.querySelectorAll('.overlay-text');

        box.forEach(element => {
            element.innerHTML = `
                <div>
                    <div>${data.title}</div>
                    <div>${data.subtitle || ""}</div>

                    <div class="divider"></div>

                    <div class="ayat">${data.arabic}</div>

                    <div class="divider"></div>

                    <div style="font-size: 20px;">${data.description}</div>
                </div>
            `;
            element.style.top = "45%";
        });

    })
    .catch(err => {
        console.log("FETCH ERROR:", err);
    });
}

$('.owl-carousel').on('changed.owl.carousel', function(event) {
let index = event.item.index;   // posisi sekarang
let total = event.item.count;   // total slide

// kalau slide terakhir (hadist/quran)
if (index === total - 1) {
	loadSlide();
}

console.log("INDEX:", index, "TOTAL:", total);
});
