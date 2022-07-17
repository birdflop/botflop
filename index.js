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
		GatewayIntentBits.MessageContent
	],
});
client.startTimestamp = Date.now();
for (const handler of fs.readdirSync('./src/handlers').filter(file => file.endsWith('.js'))) require(`./src/handlers/${handler}`)(client);