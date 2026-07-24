import {
  SlashCommandOptionsOnlyBuilder,
  PermissionsBitField,
  Message,
  Client,
  AutocompleteInteraction,
  ChatInputCommandInteraction,
  CacheType,
  SlashCommandBuilder,
  type SlashCommandSubcommandsOnlyBuilder,
} from 'discord.js';

export class PrivateCommand {
  name?: string;
  description: string;
  execute: (
    message: Message<true>,
    args: string[],
    client: Client<true>
  ) => void | Promise<void>;
}

type SlashCommandBuilderCallback = (
  slashCommandBuilder: SlashCommandBuilder
) => SlashCommandOptionsOnlyBuilder | SlashCommandSubcommandsOnlyBuilder;
export class Command<
  Cached extends CacheType = CacheType,
> extends PrivateCommand {
  name?: string | string[];
  cmd?: SlashCommandBuilderCallback;
  flags?: InteractionDeferReplyOptions.flags;
  defer?: boolean;
  category?: string;
  cooldown?: number;
  channelPermissions?: (keyof typeof PermissionsBitField.Flags)[];
  botPerms?: (keyof typeof PermissionsBitField.Flags)[];
  botChannelPerms?: (keyof typeof PermissionsBitField.Flags)[];
  dms?: boolean;
  autoComplete?: (
    client: Client<true>,
    interaction: AutocompleteInteraction<Cached>
  ) => void | Promise<void>;
  execute: (
    interaction: ChatInputCommandInteraction<Cached>,
    client: Client<true>
  ) => void | Promise<void>;
}

export class LoadedCommand extends Command {
  name: string;
}
