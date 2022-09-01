const { EmbedBuilder, ApplicationCommandOptionType, PermissionsBitField } = require('discord.js');
module.exports = {
	name: 'react',
	description: 'Adds a reaction to a message',
	ephemeral: true,
	args: true,
	usage: '<Message Link / Id (only in channel)> <Emoji>',
	options: [
		{
			'type': ApplicationCommandOptionType.String,
			'name': 'url',
			'description': 'The link to the message to add the reaction to',
			'required': true,
		},
		{
			'type': ApplicationCommandOptionType.String,
			'name': 'emoji',
			'description': 'The emoji to react with',
			'required': true,
		},
	],
	async execute(message, args, client) {
		try {
			if (!message.member.permissions
				|| (!message.member.permissions.has(PermissionsBitField.Flags.Administrator)
					&& !message.member.permissionsIn(message.channel).has(PermissionsBitField.Flags.Administrator)
				)) {
				return message.reply({ content: 'You can\'t do that! You need the Administrator permission!' });
			}

			const ReactEmbed = new EmbedBuilder()
				.setColor('Random')
				.setTitle('Reacted to message!');
			const messagelink = args[0].split('/');
			if (!messagelink[4]) messagelink[4] = message.guild.id;
			if (!messagelink[5]) messagelink[5] = message.channel.id;
			if (!messagelink[6]) messagelink[6] = args[0];
			if (messagelink[4] != message.guild.id) return message.reply({ content: 'That message is not in this server!' });
			const channel = await message.guild.channels.cache.get(messagelink[5]);
			if (!channel) return message.reply({ content: 'That channel doesn\'t exist!' });
			const msgs = await channel.messages.fetch({ around: messagelink[6], limit: 1 });
			const fetchedMsg = msgs.first();
			if (!fetchedMsg) return message.reply({ content: 'That message doesn\'t exist!' });
			await fetchedMsg.react(args[1]).catch(err => { return message.reply({ content: `Reaction failed!\n\`${err}\`\nUse an emote from a server that ${client.user.username} is in or an emoji.` }); });
			message.reply({ embeds: [ReactEmbed] });
		}
		catch (err) { client.error(err, message); }
	},
};