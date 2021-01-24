
var inmates = {};
var order = "BookDesc";

$(function(){

	console.log("LOADED...");

	//disable easy image download
	//$(this).bind("contextmenu", function(e) {
    //           e.preventDefault();
    //});

	//Grab Initial Inmate Count (Most Recent Inmates)
	$.ajax({
		type:"POST",
		url: "https://services.co.jackson.ms.us/jaildocket/_inmateList.php?Function=count",
		data: "request_type=generator",
		currentPage: 1,
		success: function(qInmates)
		{	//Setup Pagination
			console.log(qInmates);
			$('#ilpaginationWrapper').pagination({
				items: qInmates,
				itemsOnPage: 15,
				cssStyle: 'compact-theme',
				onPageClick: function(pg){
					console.log("Page: "+pg);
					//Check for Search Text
					$searchTerm = $('#inmateSearchBox').val();
					if ( $searchTerm.length > 1 ) {
						getInmates(pg,order,$searchTerm);
					} else {
						getInmates(pg,order,0);
					}
					$('#ilpaginationBottom').pagination('drawPage',pg);
				}
			});

			$('#ilpaginationBottom').pagination({
				items: qInmates,
				itemsOnPage: 15,
				cssStyle: 'compact-theme',
				onPageClick: function(pg){
					$('#ilpaginationWrapper').pagination('selectPage',pg);
					$('html,body').animate({
						scrollTop: $('.controlWrap').offset().top},200);
				}
			});
			$('#sortBy').change(function(e) {
				var optionSelected = $(this).find('option:selected');
				var selectedData = optionSelected.val();
				sortChange(selectedData);
			});

		}
	});

	$.ajax({
		type:"POST",
		dataType: "json",
		url: "https://services.co.jackson.ms.us/jaildocket/_inmateList.php?Function=list&Page=1",
		data: inmates,
		success: function(inmates)
		{
			drawInmates(inmates);
		}
	});
	var numInmates = 0;

	$('.iframe').fancybox({type:"iframe",'showCloseButton':true,'arrows' : false});

	var thread = null;

	function findMember(str) {
		$('#ilpaginationWrapper').pagination('selectPage',1);
		if ( str.length > 1 ) {
			getInmates(1,order,str);
		} else {
			getInmates(1,order,0);
		}
	  }

	  $('#inmateSearchBox').keyup(function() {
		clearTimeout(thread);
		var $this = $(this);
		thread = setTimeout(function() { findMember($this.val()); }, 500);
	  });

});


function sortChange(data) {
	//Purpose: To Handle Sort Changes
	//var sort = data.selectedData.value;
	var sort = data;
	//Globalize Sort Order (Don't Like)
	order = sort;
	//Reset Paginator to Page 1
	$('#ilpaginationWrapper').pagination('selectPage',1);
	//Get Search Value
	$searchTerm = $('#inmateSearchBox').val();
	console.log("SearchTerm: " + $searchTerm);
	//Get Data with or without Search
	if ( $searchTerm.length > 1 ) {
		getInmates(1,order,$searchTerm);
	} else {
		getInmates(1,order,0);
	}
}

function getInmates(page,order,search) {
	$.ajax({
		type:"POST",
		dataType: "json",
		url: "https://services.co.jackson.ms.us/jaildocket/_inmateList.php?Function=list&Page=" + page + "&Order=" + order + '&Search=' + search,
		data: inmates,
		success: function(inmates)
		{
			drawInmates(inmates);
		},
   failure: function(){
console.log("NOTWORKING");
}
	});

	$.ajax({
		type:"POST",
		url: "https://services.co.jackson.ms.us/jaildocket/_inmateList.php?Function=count&Search=" + search,
		data: "request_type=generator",
		success: function(qInmates)
		{
			$('#ilpaginationWrapper').pagination('updateItems',qInmates);
			$('#ilpaginationBottom').pagination('updateItems',qInmates);
		}
	});

}

function drawInmates(inmates) {
	//html = "<table id='inmateList' class='inmateTable'>";
	html = "<main class='ilcards'>";
	for (var j=0; j < inmates.length; j += 1)
		{
			var book_number = inmates[j].Book_Number;
			var first_name = inmates[j].Name_First_MI;
			var last_name = inmates[j].Name_Last;
			var row = inmates[j].RowNum;
			var mi = inmates[j].Name_Middle[0];
			if (mi = 'undefined') {mi = ''};
			var agency = inmates[j].Arrest_Agency;
			var id = inmates[j].ID_Number.trim();
			var book_date = inmates[j].BookDate;
			var arrest_date = inmates[j].ArrestDate;
			var bookD = new Date(book_date);
			var today = new Date();
			if (bookD.toLocaleDateString() == today.toLocaleDateString()) {
				$.get("https://services.co.jackson.ms.us/jaildocket/inmate/_getImage.php?ID=" + id);
				//console.log("Getting Image " + id);
			}

			html += "<article class='ilcard'> <a class='iframe' rel='modal:open' href='https://services.co.jackson.ms.us/jaildocket/inmate/_inmatedetails.php?id=" + id +"' ><img onerror='getImage(" + id + ",this)' src='https://services.co.jackson.ms.us/jaildocket/inmate/" + id + ".jpg' /></a></div>";
			html += "<div class='iltext'><a class='iframe inmateName' rel='modal:open' href='https://services.co.jackson.ms.us/jaildocket/inmate/_inmatedetails.php?id=" + id +"' >" + first_name + "<br />" + last_name + " " + mi + "</a>";
			html += "<p class='ilFieldName'>Booking Number</p><p class='ilFieldData'>" + book_number + "</p><p class='ilFieldName'>Arresting Agency</p><p class='ilFieldData'>" + agency + "</p>";
			html += "<p class='ilFieldName'>Booking Date</p><p class='ilFieldData'>" + book_date + "</p><p class='ilFieldName'>Arrest Date</p><p class='ilFieldData'>" + arrest_date + "</p>";
			html += "<div class='ilbutton'><a href='http://www.vinelink.com/vinelink/servlet/SubjectSearch?siteID=25000&agency=38&offenderID=" + id + "' target='_blank' >Request Victim Notification</a></div>";
			//html += row;
			html += "</div></article>";

		}
	html += "</main>";
	$('#inmateListWrapper').html(html);
}

function getImage(id,imgobj) {
	$.ajax({
		url: 'https://services.co.jackson.ms.us/jaildocket/inmate/_getImage.php?ID=' + id,
		type: 'GET',
		success: function(data) {
			if ( data == 'NO PICTURE FOUND' ) imgobj.src = 'https://services.co.jackson.ms.us/jaildocket/img/noimage.jpg';
		}
});
}

if(typeof String.prototype.trim !== 'function') {
  String.prototype.trim = function() {
    return this.replace(/^\s+|\s+$/g, '');
  }
}
