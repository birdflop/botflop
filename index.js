const { Client, GatewayIntentBits, Partials } = require('discord.js');
const fs = require('fs');
const client = new Client({
	partials: [
		Partials.Message,
		Partials.Channel,
		Partials.User,
	],
	intents: [
		GatewayIntentBits.Guilds,
		GatewayIntentBits.GuildMessages,
		GatewayIntentBits.GuildMembers,
		GatewayIntentBits.DirectMessages,
	],
});
client.startTimestamp = Date.now();
for (const handler of fs.readdirSync('./handlers').filter(file => file.endsWith('.js'))) require(`./handlers/${handler}`)(client);
