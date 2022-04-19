const { EmbedBuilder } = require('discord.js');
module.exports = async (client, interaction) => {
	// Check if interaction is command
	if (!interaction.isChatInputCommand()) return;

	// Get the command from the available cmds in the bot, if there isn't one, just return because discord will throw an error itself
	const command = client.commands.get(interaction.commandName);
	if (!command) return;

	// Make args variable from interaction options for compatibility with message command code
	const args = interaction.options._hoistedOptions;

	// Set args to value of options
	args.forEach(arg => args[args.indexOf(arg)] = arg.value);

	// If subcommand exists, set the subcommand to args[0]
	if (interaction.options._subcommand) args.unshift(interaction.options._subcommand);

	// Check if slash command is being sent in a DM, if so, send error message because commands in DMs are stupid
	if (interaction.channel.isDM()) return interaction.reply({ content: 'You can\'t execute commands in DMs!' });

	// Defer and execute the command
	try {
		const cmdlog = args.join ? `${command.name} ${args.join(' ')}` : command.name;
		client.logger.info(`${interaction.user.tag} issued slash command: /${cmdlog}, in ${interaction.guild.name}`.replace(' ,', ','));
		await interaction.deferReply({ ephemeral: command.ephemeral });
		interaction.reply = interaction.editReply;
		command.execute(interaction, args, client);
	}
	catch (err) {
		const interactionFailed = new EmbedBuilder()
			.setColor(Math.floor(Math.random() * 16777215))
			.setTitle('INTERACTION FAILED')
			.setAuthor({ name: interaction.user.tag, iconURL: interaction.user.avatarURL() })
			.addFields({ name: '**Type:**', value: 'Slash' })
			.addFields({ name: '**Interaction:**', value: command.name })
			.addFields({ name: '**Error:**', value: `\`\`\`\n${err}\n\`\`\`` })
			.addFields({ name: '**Guild:**', value: interaction.guild.name })
			.addFields({ name: '**Channel:**', value: interaction.channel.name });
		interaction.user.send({ embeds: [interactionFailed] }).catch(err => client.logger.warn(err));
		client.logger.error(err.stack);
	}
};