const createField = require('./createField.js');
module.exports = function eval_field(Embed, option, option_name, plugins, server_properties, bukkit, spigot, paper, purpur, client) {
	const dict_of_vars = { 'plugins': plugins, 'server_properties': server_properties, 'bukkit': bukkit, 'spigot': spigot, 'paper': paper, 'purpur': purpur };
	option.forEach(option_data => {
		let add_to_field = true;
		option_data.expressions.forEach(expression => {
			Object.keys(dict_of_vars).forEach(config_name => {
				if (expression.includes(config_name) && !dict_of_vars[config_name]) add_to_field = false;
			});
			try {
				if (add_to_field && !eval(expression)) add_to_field = false;
			}
			catch (e) {
				client.logger.warn(e);
				add_to_field = false;
			}
		});
		Object.keys(dict_of_vars).forEach(config_name => {
			if (add_to_field && option_data.value.includes(config_name) && !dict_of_vars[config_name]) add_to_field = false;
		});
		if (add_to_field) {
			option_data.name = option_name;
			Embed.addFields(createField(option_data));
		}
	});
};