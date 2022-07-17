/* eslint-disable no-trailing-spaces */
const { MessageEmbed } = require('discord.js');
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
			'type': 'STRING',
			'name': 'address',
			'description': 'The IP address of the server',
			'required': true,
		}
	],
	async execute(message, args, client) {
		try {
			// Create embed with ping information and add ping again button
			const ErrorEmbed = new MessageEmbed()
				.setColor('RED')
				.setTitle('Error!');
			
			const address = args[0];
			console.log(address)
			await getServerStatus(message, client, address);
		}
		catch (err) { client.logger.error(err.stack); }
	},
};