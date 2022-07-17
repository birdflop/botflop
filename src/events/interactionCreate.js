const { MessageEmbed } = require('discord.js');
module.exports = async (client, interaction) => {
	// Check if interaction is command
	if (!interaction.isCommand()) return;

	// Get the command from the available cmds in the bot, if there isn't one, just return because discord will throw an error itself
	const command = client.commands.get(interaction.commandName);
	if (!command) return;

	// Make args variable from interaction options for compatibility with message command code
	const args = interaction.options._hoistedOptions;

	// Set args to value of options
	args.forEach(arg => args[args.indexOf(arg)] = arg.value);

	// Defer and execute the command
	try {
		const cmdlog = args.join ? `${command.name} ${args.join(' ')}` : command.name;
		client.logger.info(`${interaction.user.tag} issued slash command: /${cmdlog}, in ${interaction.guild.name}`.replace(' ,', ','));
		await interaction.deferReply({ ephemeral: command.ephemeral });
		interaction.reply = interaction.editReply;
		command.execute(interaction, args, client);
	}
	catch (err) {
		const interactionFailed = new MessageEmbed()
			.setColor(Math.floor(Math.random() * 16777215))
			.setTitle('INTERACTION FAILED')
			.setAuthor({ name: interaction.user.tag, iconURL: interaction.user.avatarURL() })
			.addFields([
				{ name: '**Type:**', value: 'Slash' }, { name: '**Interaction:**', value: command.name },
			]);
		if (!interaction.guild == null) {
			interactionFailed.addFields([
				{ name: '**Guild:**', value: interaction.guild.name },
				{ name: '**Channel:**', value: interaction.channel.name },
				{ name: '**Error:**', value: `\`\`\`\n${err}\n\`\`\`` },
			]);
		}
		else {
			interactionFailed.addFields([
				{ name: '**Error:**', value: 'You must send this slash command inside of a guild!' },
			]);
		}
		interaction.user.send({ embeds: [interactionFailed] }).catch(err => client.logger.warn(err));
		client.logger.error(err.stack);
	}
};