var markers, map;


function computeBounds(data){
  var bounds = new mapboxgl.LngLatBounds()
  for (var _i = 0, id = DATA.ID_LIST[_i]; _i<DATA.ID_LIST.length; id=DATA.ID_LIST[++_i]){
    bounds.extend(new mapboxgl.LngLat(data[id].long, data[id].lat));
  }
  return bounds;
}


fetch(new Request('/data/locations.json')).then(function(response) {
  return response.json();
}).then(function(data) {
  mapboxgl.accessToken = DATA.ACCESS_TOKEN;
  var marker_elements = {};
  var markers = {}
  for (var _i = 0, id = DATA.ID_LIST[_i]; _i<DATA.ID_LIST.length; id=DATA.ID_LIST[++_i]){
    marker_elements[id] = document.createElement('div');
    marker_elements[id].setAttribute('style', `
      background-image: url('${data[id].picture_url}');
      background-size: cover;
      width: 40px;
      height: 40px;
      border-radius: 50%;`);
    markers[id] = new mapboxgl.Marker(marker_elements[id]);
    markers[id].setLngLat([data[id].long, data[id].lat]);
  }
  map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/dark-v9',
    bounds: computeBounds(data),
    fitBoundsOptions: {padding: 50, maxZoom: 19},
    });
  for (var _i = 0, id = DATA.ID_LIST[_i]; _i<DATA.ID_LIST.length; id=DATA.ID_LIST[++_i]){
    markers[id].addTo(map);
  }
});


setInterval(function(){
  fetch(new Request('/data/locations.json')).then(function(response) {
    return response.json();
  }).then(function(data) {
    for (var _i = 0, id = DATA.ID_LIST[_i]; _i<DATA.ID_LIST.length; id=DATA.ID_LIST[++_i]){
      markers[id].setLngLat([data[id].long, data[id].lat]);
    }
    map.fitBounds(
      computeBounds(data),
      {padding: 50, maxZoom: 19}
    );
  })
}, 10000);