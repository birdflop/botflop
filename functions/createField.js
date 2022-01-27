module.exports = function createField(option) {
	const field = { name: option.name, value: option.value, inline: true };
	if (option.prefix) field.name = option.prefix + ' ' + field.name;
	if (option.suffix) field.name = field.name + option.suffix;
	if (option.inline) field.inline = option.inline;
	return field;
};