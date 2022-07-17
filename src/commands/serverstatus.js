/* eslint-disable no-trailing-spaces */
const { EmbedBuilder, ApplicationCommandOptionType } = require('discord.js');
const getServerStatus = require('../functions/getServerStatus');
module.exports = {
	name: 'serverstatus',
	description: 'Minecraft server status!',
	ephemeral: false,
	aliases: ['status'],
	args: true,
	usage: '<Message Link / Id (only in channel)> <Emoji>',
	options: [
		{
			'type': ApplicationCommandOptionType.String,
			'name': 'address',
			'description': 'The IP address of the server',
			'required': true,
		}
	],
	async execute(message, args, client) {
		try {
			// Create embed with ping information and add ping again button
			const ErrorEmbed = new EmbedBuilder()
				.setColor('Red')
				.setTitle('Error!');
			
			const address = args[0];
			await getServerStatus(message, client, address);
		}
		catch (err) { client.logger.error(err.stack); }
	},
};