

Date.prototype.objectReference;
Date.prototype.parse = function(){
	try {
		str = this.objectReference.value.split("-");
		this.setYear(str[0]);
		this.setMonth(str[1]-1);
		this.setDate(str[2]);
	}
	catch (e){
		alert("Incorrect date");
	}
	if (isNaN(this.getYear()) || isNaN(this.getMonth()) || isNaN(this.getDate())){
		alert("Incorrect date");
		this.setTime(Date.now());
		this.toDateString();
	}
}
function justify(value){
	if (value<10 && value>0){
		return ("0"+value);
	}
	else {
		return value;
	}
}
Date.prototype.toDateString = function(){
	var str = (this.getFullYear())+"-"
		+justify(this.getMonth()+1)+"-"
		+justify(this.getDate());
	this.objectReference.value = str;
	return str;
}
Date.prototype.plusDay = function(){
	this.parse();
	this.setDate(this.getDate()+1);
	this.toDateString();
}
Date.prototype.minusDay = function(){
	this.parse();
	this.setDate(this.getDate()-1);
	this.toDateString();
}
Date.prototype.plusWeek = function(){
	this.parse();
	this.setDate(this.getDate()+7);
	this.toDateString();
}
Date.prototype.minusWeek = function(){
	this.parse();
	this.setDate(this.getDate()-7);
	this.toDateString();
}
Date.prototype.plusMonth = function(){
	this.parse();
	this.setMonth(this.getMonth()+1);
	this.toDateString();
}
Date.prototype.minusMonth = function(){
	this.parse();
	this.setMonth(this.getMonth()-1);
	this.toDateString();
}
