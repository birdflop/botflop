const analyzeTimings = require('../functions/analyzeTimings');
const { createPaste } = require('hastebin');
const fetch = (...args) => import('node-fetch').then(({ default: e }) => e(...args));
const { EmbedBuilder, PermissionsBitField } = require('discord.js');
module.exports = async (client, message) => {
	if (message.author.bot) return;

	// If the bot can't read message history or send messages, don't execute a command
	if (!message.guild.me.permissionsIn(message.channel).has(PermissionsBitField.Flags.SendMessages)
	|| !message.guild.me.permissionsIn(message.channel).has(PermissionsBitField.Flags.ReadMessageHistory)) return;

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

	// Binflop
	if (message.attachments.size > 0) {
		const url = message.attachments.first().url.toLowerCase();
		const filetypes = ['.log', '.txt', '.json', '.yml', '.yaml', '.css', '.py', '.js', '.sh', '.config', '.conf'];
		if (!url.endsWith('.html')) {
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

				const link = await createPaste(text, { server: 'https://bin.birdflop.com' });
				let response = `${link}\nRequested by ${message.author}`;
				if (truncated) response = response + '\n(file was truncated because it was too long.)';

				const Embed = new EmbedBuilder()
					.setTitle('Please use a paste service')
					.setColor(0x1D83D4)
					.setDescription(response);
				await message.channel.send({ embeds: [Embed] });
				client.logger.info(`File uploaded by ${message.author.tag} (${message.author.id}): ${link}`);
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

			const link = await createPaste(text, { server: 'https://bin.birdflop.com' });
			let response = `${link}\nRequested by ${message.author}`;
			if (truncated) response = response + '\n(file was truncated because it was too long.)';

			const Embed = new EmbedBuilder()
				.setTitle('Pastebin is blocked in some countries')
				.setColor(0x1D83D4)
				.setDescription(response);
			await message.channel.send({ embeds: [Embed] });
			client.logger.info(`Pastebin converted from ${message.author.tag} (${message.author.id}): ${link}`);
		}
	}

	// Get the prefix
	let prefix = process.env.PREFIX;

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
				const filter = i => i.user.id == message.member.id && i.customId.startsWith('timings_');
				const collector = timingsmsg.createMessageComponentCollector({ filter, time: 300000 });
				collector.on('collect', async i => {
					// Defer button
					i.deferUpdate();

					// Get the embed and clear the fields
					const TimingsEmbed = new EmbedBuilder(timingsmsg.embeds[0].toJSON());
					TimingsEmbed.setFields(...issues);

					// Get page from footer
					const footer = TimingsEmbed.toJSON().footer.text.split(' • ');
					let page = parseInt(footer[footer.length - 1].split('Page ')[1].split(' ')[0]);

					// Add/Remove page depending on the customId
					if (i.customId == 'timings_next') page = page + 1;
					if (i.customId == 'timings_prev') page = page - 1;

					// Turn to last page if page is 0 and turn to first page if page is more than the max page
					if (page == 0) page = Math.ceil(issues.length / 12);
					if (page > Math.ceil(issues.length / 12)) page = 1;

					// idk what happened here but it works
					const index = page * 12;
					TimingsEmbed.toJSON().fields.splice(0, index - 12);
					TimingsEmbed.toJSON().fields.splice(index, issues.length);
					footer[footer.length - 1] = `Page ${page} of ${Math.ceil(issues.length / 12)}`;
					TimingsEmbed.setFooter({ text: footer.join(' • ') });

					// Send the embed
					timingsmsg.edit({ embeds: [TimingsEmbed] });
				});
			}

		}
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
			.setColor(Math.floor(Math.random() * 16777215))
			.setTitle('INTERACTION FAILED')
			.setAuthor({ name: message.author.tag, iconURL: message.author.avatarURL() })
			.addFields({ name: '**Type:**', value: 'Message' })
			.addFields({ name: '**Guild:**', value: message.guild.name })
			.addFields({ name: '**Channel:**', value: message.channel.name })
			.addFields({ name: '**INTERACTION:**', value: prefix + command.name })
			.addFields({ name: '**Error:**', value: `\`\`\`\n${err}\n\`\`\`` });
		client.guilds.cache.get('811354612547190794').channels.cache.get('830013224753561630').send({ content: '<@&839158574138523689>', embeds: [interactionFailed] });
		message.author.send({ embeds: [interactionFailed] }).catch(err => client.logger.warn(err));
		client.logger.error(err.stack);
	}
};