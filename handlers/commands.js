const { readdirSync } = require('fs');
const { Collection } = require('discord.js');
module.exports = client => {
	let amount = 0;
	client.cooldowns = new Collection();
	client.commands = new Collection();
	const commandFiles = readdirSync('./commands');
	for (const file of commandFiles) {
		const command = require(`../commands/${file}`);
		client.commands.set(command.name, command);
		amount = amount + 1;
	}
	client.logger.info(`${amount} commands loaded`);
};