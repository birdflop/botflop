const { EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
const YAML = require('yaml');
const fs = require('fs');
const createField = require('./createField.js');
const evalField = require('./evalField.js');
const Pbf = require('pbf');
const { HeapData, SamplerData } = require('../protos');

// Function to parse the data payload from a request given the schema type
function parse(buf, schema) {
	const pbf = new Pbf(new Uint8Array(buf));
	return schema.read(pbf);
}

module.exports = async function analyzeProfile(message, client, args) {
	const author = message.author ?? message.user;
	const ProfileEmbed = new EmbedBuilder()
		.setDescription('These are not magic values. Many of these settings have real consequences on your server\'s mechanics. See [this guide](https://eternity.community/index.php/paper-optimization/) for detailed information on the functionality of each setting.')
		.setFooter({ text: `Requested by ${author.tag}`, iconURL: author.avatarURL() });

	let url;
	const fields = [];

	args.forEach(arg => {
		if (message.commandName && (arg.startsWith('https://timin') || arg.startsWith('https://www.spigotmc.org/go/timings?url=') || arg.startsWith('https://spigotmc.org/go/timings?url='))) {
			ProfileEmbed.addFields([{ name: '⚠️ Timings Report', value: 'This is a Timings report. Use /timings instead for this type of report.' }]);
			return [{ embeds: [ProfileEmbed] }];
		}
	});

	if (!url) return false;

	// Start typing
	await message.channel.sendTyping();

	client.logger.info(`Spark Profile analyzed from ${author.tag} (${author.id}): ${url}`);

	let error;
	const code = url.replace('https://spark.lucko.me/', '');
	const bytebin = `https://bytebin.lucko.me/${code}`;
	let sampler;
	try {
		const req = await fetch(bytebin);
		const buf = await req.arrayBuffer();
		sampler = parse(buf, SamplerData);
	}
	catch (err) {
		error = err;
	}

	ProfileEmbed.setAuthor({ name: 'Spark Profile Analysis', iconURL: 'https://i.imgur.com/deE1oID.png', url: url });

	if (error) {
		ProfileEmbed.addFields([
			{ name: '❌ Invalid Profile', value: 'Create a new Spark Profile.' },
			{ name: '❌ Error', value: `\`\`\`\n${error}\n\`\`\`` },
		]);
		return [{ embeds: [ProfileEmbed] }];
	}

	console.log(sampler);
};