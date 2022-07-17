const { Client } = require('discord.js');
const fs = require('fs');
const client = new Client({
	partials: [
		'MESSAGE',
		'CHANNEL',
		'USER',
	],
	intents: [
		'GUILDS',
		'GUILD_MESSAGES',
		'GUILD_MEMBERS',
		'DIRECT_MESSAGES',
	],
});
client.startTimestamp = Date.now();
for (const handler of fs.readdirSync('./src/handlers').filter(file => file.endsWith('.js'))) require(`./src/handlers/${handler}`)(client);