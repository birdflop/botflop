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

	const url = args[0];
	const code = url.replace('https://spark.lucko.me/', '');
	const bytebin = `https://bytebin.lucko.me/${code}`;
	const req = await fetch(bytebin);
	const buf = await req.arrayBuffer();
	const sampler = parse(buf, SamplerData);
	console.log(sampler);
};