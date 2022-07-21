const analyzeTimings = require('../functions/analyzeTimings');
const { createPaste } = require('hastebin');
const fetch = (...args) => import('node-fetch').then(({ default: e }) => e(...args));
const { EmbedBuilder, PermissionsBitField } = require('discord.js');
module.exports = async (client, message) => {
	if (message.author.bot) return;

	// If the bot can't read message history or send messages, don't execute a command
	if (message.guild && (!message.guild.members.me.permissionsIn(message.channel).has(PermissionsBitField.Flags.SendMessages) || !message.guild.members.me.permissionsIn(message.channel).has(PermissionsBitField.Flags.ReadMessageHistory))) return;

	// make a custom function to replace message.reply
	// this is to send the message to the channel without a reply if reply fails
	message.msgreply = message.reply;
	message.reply = function reply(object) {
		return message.msgreply(object).catch(err => {
			client.logger.warn(err);
			return message.channel.send(object).catch(err => {
				client.logger.error(err.stack);
			});
		});
	};

	// Get the prefix
	let prefix = process.env.PREFIX;

	try {
		// Binflop
		if (message.attachments.size > 0) {
			const url = message.attachments.first().url;
			const filetypes = ['.log', '.txt', '.json', '.yml', '.yaml', '.css', '.py', '.js', '.sh', '.config', '.conf'];
			if (!url.endsWith('.html')) {
				if (!message.attachments.first().contentType) return;
				const filetype = message.attachments.first().contentType.split('/')[0];
				if (filetypes.some(ext => url.endsWith(ext)) || filetype == 'text') {
					// Start typing
					await message.channel.sendTyping();

					// fetch the file from the external URL
					const res = await fetch(url);

					// take the response stream and read it to completion
					let text = await res.text();

					let truncated = false;
					if (text.length > 100000) {
						text = text.substring(0, 100000);
						truncated = true;
					}

					let response = await createPaste(text, { server: 'https://bin.birdflop.com' });
					if (truncated) response = response + '\n(file was truncated because it was too long.)';

					const PasteEmbed = new EmbedBuilder()
						.setTitle('Please use a paste service')
						.setColor(0x1D83D4)
						.setDescription(response)
						.setFooter({ text: `Requested by ${message.author.tag}`, iconURL: message.author.avatarURL() });
					await message.channel.send({ embeds: [PasteEmbed] });
					client.logger.info(`File uploaded by ${message.author.tag} (${message.author.id}): ${response}`);
				}
			}
		}

		// Pastebin is blocked in some countries
		const words = message.content.replace(/\n/g, ' ').split(' ');
		for (const word of words) {
			if (word.startsWith('https://pastebin.com/') && word.length == 29) {
				// Start typing
				await message.channel.sendTyping();

				const key = word.split('/')[3];
				const res = await fetch(`https://pastebin.com/raw/${key}`);
				let text = await res.text();

				let truncated = false;
				if (text.length > 100000) {
					text = text.substring(0, 100000);
					truncated = true;
				}

				let response = await createPaste(text, { server: 'https://bin.birdflop.com' });
				if (truncated) response = response + '\n(file was truncated because it was too long.)';

				const PasteEmbed = new EmbedBuilder()
					.setTitle('Pastebin is blocked in some countries')
					.setColor(0x1D83D4)
					.setDescription(response)
					.setFooter({ text: `Requested by ${message.author.tag}`, iconURL: message.author.avatarURL() });
				await message.channel.send({ embeds: [PasteEmbed] });
				client.logger.info(`Pastebin converted from ${message.author.tag} (${message.author.id}): ${response}`);
			}
		}

		// Use mention as prefix instead of prefix too
		if (message.content.replace('!', '').startsWith(`<@${client.user.id}>`)) prefix = message.content.split('>')[0] + '>';

		// If the message doesn't start with the prefix (mention not included), check for timings report
		if (!message.content.startsWith(process.env.PREFIX)) {
			const timingsresult = await analyzeTimings(message, client, words);
			if (timingsresult) {
				const timingsmsg = await message.reply(timingsresult[0]);

				// Get the issues from the timings result
				const issues = timingsresult[1];
				if (issues) {
					const filter = i => i.user.id == message.author.id && i.customId.startsWith('timings_');
					const collector = timingsmsg.createMessageComponentCollector({ filter, time: 300000 });
					collector.on('collect', async i => {
						// Defer button
						i.deferUpdate();

						// Get the embed
						const TimingsEmbed = new EmbedBuilder(i.message.embeds[0].toJSON());
						const footer = TimingsEmbed.toJSON().footer;

						// Calculate total amount of pages and get current page from embed footer
						const text = footer.text.split(' • ');
						const lastPage = parseInt(text[text.length - 1].split('Page ')[1].split(' ')[0]);
						const maxPages = parseInt(text[text.length - 1].split('Page ')[1].split(' ')[2]);

						// Get next page (if last page, go to pg 1)
						const page = i.customId == 'timings_next' ? lastPage == maxPages ? 1 : lastPage + 1 : lastPage - 1 ? lastPage - 1 : maxPages;
						const end = page * 12;
						const start = end - 12;
						const fields = issues.slice(start, end);

						// Update the embed
						text[text.length - 1] = `Page ${page} of ${Math.ceil(issues.length / 12)}`;
						TimingsEmbed
							.setFields(fields)
							.setFooter({ iconURL: footer.iconURL, text: text.join(' • ') });

						// Send the embed
						timingsmsg.edit({ embeds: [TimingsEmbed] });
					});
				}
			}
		}
	}
	catch (err) {
		client.logger.error(err.stack);
	}

	// If message doesn't start with the prefix, if so, return
	if (!message.content.startsWith(prefix)) return;

	// Get args by splitting the message by the spaces and getting rid of the prefix
	const args = message.content.slice(prefix.length).trim().split(/ +/);

	// Get the command name from the fist arg and get rid of the first arg
	const commandName = args.shift().toLowerCase();

	// Get the command from the commandName, if it doesn't exist, return
	const command = client.commands.get(commandName) || client.commands.find(cmd => cmd.aliases && cmd.aliases.includes(commandName));

	// If the command doesn't exist, find timings report
	if (!command || !command.name) return;

	// Start typing (basically to mimic the defer of interactions)
	await message.channel.sendTyping();

	// Check if args are required and see if args are there, if not, send error
	if (command.args && args.length < 1) {
		const Usage = new EmbedBuilder()
			.setColor(0x5662f6)
			.setTitle('Usage')
			.setDescription(`\`${prefix + command.name + ' ' + command.usage}\``);
		return message.reply({ embeds: [Usage] });
	}

	// execute the command
	try {
		client.logger.info(`${message.author.tag} issued message command: ${message.content}, in ${message.guild.name}`);
		command.execute(message, args, client);
	}
	catch (err) {
		const interactionFailed = new EmbedBuilder()
			.setColor('Random')
			.setTitle('INTERACTION FAILED')
			.setAuthor({ name: message.author.tag, iconURL: message.author.avatarURL() })
			.addFields([
				{ name: '**Type:**', value: 'Message' },
				{ name: '**Guild:**', value: message.guild.name },
				{ name: '**Channel:**', value: message.channel.name },
				{ name: '**INTERACTION:**', value: prefix + command.name },
				{ name: '**Error:**', value: `\`\`\`\n${err}\n\`\`\`` }]);
		client.guilds.cache.get('811354612547190794').channels.cache.get('830013224753561630').send({ content: '<@&839158574138523689>', embeds: [interactionFailed] });
		message.author.send({ embeds: [interactionFailed] }).catch(err => client.logger.warn(err));
		client.logger.error(err.stack);
	}
};