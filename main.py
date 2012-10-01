#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
class MainPageHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write(MAINPAGE);

class NotAMapHandler(webapp.RequestHandler):
    def get(self):
	self.response.headers['Content-Type'] = 'text/javascript'
        self.response.out.write(JS);


def main():
    application = webapp.WSGIApplication([('/notamap.js', NotAMapHandler),
    					  ('/', MainPageHandler)])
    util.run_wsgi_app(application)



JS='''function notAMap(static) {
	function removeOldMaps() {
		var header = document.getElementById("notamap_header");
		if (header) {
			header.parentNode.removeChild(header);
		}
		var els = document.getElementsByTagName("div");
		for (var i=els.length-1; i>=0;i--) {
			if (els[i].className == "notamap") {
				els[i].parentNode.removeChild(els[i]);
			}
		}
	}

	function addHeader() {
		var maintable = getMainTable();
		var div = document.createElement("div");
		div.id="notamap_header";
		div.innerHTML = '<h2><a href="http://notamap-nl.appspot.com/" target="_blank">Notamap</a></h2><p>Note: the maps displayed with the notams are for informational purposes only. Please always confirm that they show the correct information!</p><a href="javascript:void(0);">'+(static?"dynamic google maps":"static google maps")+'</a><a href="javascript:void(0);">Printable version</a>'+(navigator.userAgent.indexOf("Chrome/") != -1 ? "<p>Note: Some versions of Chrome seem to contain a bug that will mess up printing these notams and images correctly. Things do seem to work in IE, Firefox, Safari and most likely others, so try one of those if you're having problems.</p>" : "")+"<p>See http://notamap-nl.appspot.com/</p>"
		maintable.parentNode.insertBefore(div, maintable);
		var links = div.getElementsByTagName("a");
		links[1].onclick = function () {notAMap(!static);};
		links[2].onclick = printableVersion;
	}

	function printableVersion() {
		var div = document.createElement("div");
		div.style.display="none";
		document.body.appendChild(div);
		while (document.body.children[0] != div) {
			div.appendChild(document.body.children[0]);
		}
		div.style.display="none";

		var header = document.getElementById("notamap_header");
		document.body.appendChild(header);
		var hr = document.createElement("hr");
		hr.style.width = 1024;
		document.body.appendChild(hr);
		document.body.appendChild(getMainTable());

		var links = header.getElementsByTagName("a");
		links[2].innerHTML = "Original version (reload)";
		links[2].onclick = function () {window.location.reload();};
	}

	/**
	 * Gets the main table that contains the notams
	 */
	function getMainTable() {
		var myform = document.getElementsByName("FORM")[0];
		return myform.parentNode;
	}


	function initializeNotAMap() {
		removeOldMaps()
		addHeader()
		var mapregex = /([0-9]{2})([0-9]{2})([0-9]{2})?([0-9]{2})?([NS]) ?([0-9]{3})([0-9]{2})([0-9]{2})?([0-9]{2})?([EW])([ ]+RAD(IUS)? ([0-9]+(.[0-9]+)?)NM)?/g;
		var nmile = 1852; // meters per nautical mile
                var minmapdiag=25000; //25 km minimum map diagonal
		var elements = document.getElementsByTagName("pre");
		for (var i=0;i<elements.length;i++) {
			var html = elements[i].innerHTML.replace(RegExp(String.fromCharCode(10),"g"), " ").replace(RegExp(String.fromCharCode(13),"g"), " "); 
			if (html.search(mapregex) != -1){
				var div = document.createElement("div");
				div.className="notamap"
				elements[i].parentNode.appendChild(div);

				var latlongs = [];
				var markers = [];
				html.replace(mapregex, function (full,d1,m1,s1,h1,b,d2,m2,s2,h2,l, radius, ius, nm) {
					var lat=parseInt(d1)+parseInt(m1)/60+(parseInt(s1)?parseInt(s1)/3600:0)+(parseInt(h1)?parseInt(h1)/360000:0)*(b=="N"?1:-1);
					var lng=parseInt(d2)+parseInt(m2)/60+(parseInt(s2)?parseInt(s2)/3600:0)+(parseInt(h2)?parseInt(h2)/360000:0)*(l=="E"?1:-1);
						var latlong = new google.maps.LatLng(lat, lng);
					if (radius) {
						for (var a=0;a<360; a+=10) {
							latlongs.push(google.maps.geometry.spherical.computeOffset(latlong, nm*nmile, a));
						}
					} else {
						latlongs.push(latlong);
					}
					markers.push(new google.maps.Marker({
						position: latlong,
						title: full
					}));
				});

				var bounds = new google.maps.LatLngBounds(latlongs[0], latlongs[0]);
				for (var j=1;j<latlongs.length;j++){
					bounds.extend(latlongs[j]);
				}
				var center = bounds.getCenter();
				bounds.extend(google.maps.geometry.spherical.computeOffset(center, minmapdiag/2, 305));
				bounds.extend(google.maps.geometry.spherical.computeOffset(center, minmapdiag/2, 125));

				if (static) {
					var url = "http://maps.google.com/maps/api/staticmap?size=552x400&sensor=false";
					
					if (latlongs.length > 2) {
						path = "color:0xFF0000C0|weight:2|fillcolor:0xFF000050"
						for (var j=0; j<latlongs.length; j++) {
							path+="|"+latlongs[j].toUrlValue();
						}
						path+="|"+latlongs[0].toUrlValue(); // back to where we came from
						url += "&path="+encodeURIComponent(path);
					}
					url_markers = "color:red"
					for (var j=0; j<markers.length;j++) {
						url_markers += "|"+markers[j].getPosition().toUrlValue();
					}
					url += "&markers="+encodeURIComponent(url_markers);
					url += "&visible="+encodeURIComponent(bounds.getNorthEast().toUrlValue()+"|"+bounds.getSouthWest().toUrlValue());
					url += "&center="+encodeURIComponent(bounds.getCenter().toUrlValue());
					div.innerHTML = '<img src="'+url+'">';
					
					var url = "http://maps.google.com/maps/api/staticmap?size=120x120&sensor=false";
					var diag = 3 * google.maps.geometry.spherical.computeLength([bounds.getNorthEast(), bounds.getSouthWest()]);
					url += "&visible="+encodeURIComponent(google.maps.geometry.spherical.computeOffset(center, diag/2, 315).toUrlValue()+"|"+google.maps.geometry.spherical.computeOffset(center, diag/2, 135).toUrlValue());
					url += "&path="+encodeURIComponent("color:0x000000C0|weight:1|fillcolor:0xFFFFFF20");
					url += encodeURIComponent("|"+bounds.getNorthEast().toUrlValue());
					url += encodeURIComponent("|"+bounds.getNorthEast().lat()+","+bounds.getSouthWest().lng());
					url += encodeURIComponent("|"+bounds.getSouthWest().toUrlValue());
					url += encodeURIComponent("|"+bounds.getSouthWest().lat()+","+bounds.getNorthEast().lng());
					url += encodeURIComponent("|"+bounds.getNorthEast().toUrlValue());

					div.innerHTML += '<img src="'+url+'" class="notamap_mini">'
				} else {
			
					var myOptions = {
						zoom: 11,
						center: bounds.getCenter(),
						mapTypeId: google.maps.MapTypeId.ROADMAP
					}
					var map = new google.maps.Map(div, myOptions);
					map.fitBounds(bounds);
		
					if (latlongs.length > 2) {
						new google.maps.Polygon({
							paths: latlongs,
							map: map,
							strokeColor: "#FF0000",
							strokeOpacity: 0.8,
							strokeWeight: 2,
							fillColor: "#FF0000",
							fillOpacity: 0.35
						});
					}
					for (var j=0;j<markers.length;j++){
						markers[j].setMap(map);
					}
				}
			}
		}
	}

	if (1 || ! window.google || !window.google.maps || !window.google.maps.geometry) {
		var script = document.createElement("script");
		script.type = "text/javascript";
		window.mycallback_notamap = initializeNotAMap;
		script.src = "http://maps.google.com/maps/api/js?sensor=false&libraries=geometry&callback=mycallback_notamap";
		document.body.appendChild(script);

		
		var css = ".notamap {position: relative; height: 400px;} .notamap_mini {position: absolute; top: 279px; left: 431px; border-left: 1px solid black; border-top: 1px solid black;} #notamap_header a {padding-right: 20px;}  #notamap_header h2 {text-align: center;} #notamap_header {width: 600px; padding-bottom: 5px; margin-bottom: 7px; border: 1px solid black;} td {vertical-align: top;}";
		var div = document.createElement("div");
		div.innerHTML='<p>x</p><style>'+css+'</style>';
		document.body.appendChild(div.childNodes[1]); //work around for inserting style in all browsers including IE
	} else {
		initializeNotAMap();
	}
}
if (confirm("Notamap adds maps to notams. However, it can't be guaranteed that these maps are accurate. It may even be possible (although unlikely) that the maps display over actual notams. Do you understand that it's your own responsibility to read and understand the notams before running Notamap?")) {
	notAMap(true);
}
'''

MAINPAGE='''
<html>
<body>
<h1>notamap</h1>
<p>
Notams (at least Dutch Notams) contain a lot of coordinates, such as 52491811N 005172691E. Obviously we all learned how to plot these on our maps, but sometimes it just feels like a lot of work, with very little reward (since 99% of the time you won't come close to the point mentioned anyway). I tried to do some quick workarounds to mapping them by hand, but unfortunately Google Maps doesn't recognise coordinates in this format (it wants you to rewrite them as: 52 49' 18.11"N 005 17' 26.91"E, which is about as much work as just locating them by hand).
</p>
<p>
I just wanted something easier. After some experimenting, I got to write a bookmarklet that displays the points directly on a map, and insert these maps in the notams for easy reference. So even high up in the air, I can now quickly see whether I'm entering a notam controlled area. Below a screenshot from the homebriefing site after the notamap bookmarklet was run.
</p>
<img src="/statics/example.png">
<p>
A bookmarklet is a bookmark (like any other bookmark it can be put in several places in your browser; a toolbar, in the menu, or even under a hotkey). However where a normal bookmark takes you to another site, a bookmarklet runs some code on the current page you're viewing. As you will see in the rest of the description, after you've installed the bookmarklet, all you have to do is generate the notams the way you're used to, and then click the bookmarklet, and voila, the maps appear! This works in most browsers, and was tested in recent versions of Internet Explorer, Firefox, Safari and Chrome.
</p>
<p>
Please note that although the bookmarklet does its best to map the notams, it's not perfect, nor a replacement for reading the notams or common sense. Don't use the maps as your only source of information, and always doublecheck that the maps are accurate and indeed indicate all information that was contained in the notam, and read the notams before running Notamap, to make sure that Notamap didn't hide any information! <a href="/statics/example_wrong.png">See an example of where the map gives misleading information and the notam needs to be read!</a>
</p>
<h2>Installing and using</h2>
<p>Okay, so here we go, this is the bookmarklet: <a href="javascript:var script = document.createElement('script'); script.type = 'text/javascript'; script.src = 'https://notamap-nl.appspot.com/notamap.js?v='+Math.random(); document.body.appendChild(script);undefined;">Notamap</a>. Note that clicking this link will not do anything on this page (or perhaps mess up the page if you're unlucky; you can however always reload the page). To install the bookmarklet, drag the link (<--- the blue link called "Notamap" earlier) to your bookmark toolbar. If your bookmark toolbar is not visible, <a href="http://www.delicious.com/help/bookmarklets" target="_blank">see here how to make it visible</a>. After you have dragged the link to your toolbar, you should see "Notamap" in the toolbar, and you're done installing.
</p>
<p>After installing the bookmarklet, getting your maps with the notams is as easy as requesting the notams on the ais website, and choosing "display in browser (HTML)". Now when you see the notams, click the "Notamap" bookmarklet in your bookmarks toolbar. An extra header is added to the notams, and each notam with coordinates in it will get an accompanying map (if you have Internet Explorer, you might be served <a href="/statics/ie_warning.png">a note about secure and insecure page parts</a>; in this case you'll have to click "No" for Notamap to work). Note that to print the notams, you'll have to use the link to the printable format in the Notamap box, or a new page without the maps will be generated.
</p>
<p>Good luck, and let me know how it works for you</p>
<h2>Other info</h2>
<p>The bookmarklet was written and is (hopefully) being maintained by Reinoud Elhorst. Obviously it comes without any guarantee about its correct workings; it may stop working if the homebriefing site is changed or notams are being displayed in some other format; all I can guarantee is that I will most likely try to get it working whenever I need it myself. Having said that, please let me know if you run into a problem with it (or want to share something else with me):
<script>
	document.write("notamap".String,fromCharCode(42)."claude);
	document.write(".nl");
</script>
 (messages may be either in Dutch or English). I fly myself at Hilversum, in SEP-planes.
</p>
<p>
The name Notamap is obviously a contraction of Notam and Map, however, the pronounciacion is as "not-a-map". This should remind everybody that the information displayed in the maps is not authoritive, and the maps are only for convenience.
</p>
</body>
</html>
'''

if __name__ == '__main__':
    main()

