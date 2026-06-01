import {
  EmbedBuilder as DiscordEmbedBuilder,
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  type ColorResolvable,
  type APIEmbedField,
  type MessageActionRowComponentBuilder,
} from "discord.js";

interface ButtonConfig {
  label: string;
  customId: string;
  style?: ButtonStyle;
  url?: string;
  disabled?: boolean;
}

export class EmbedBuilder {
  private static readonly colors = {
    primary: "#5865F2" as ColorResolvable,
    success: "#57F287" as ColorResolvable,
    warning: "#FEE75C" as ColorResolvable,
    error: "#ED4245" as ColorResolvable,
    info: "#00A8FC" as ColorResolvable,
  };

  private embed: DiscordEmbedBuilder;
  private buttons: ButtonConfig[] = [];

  constructor() {
    this.embed = new DiscordEmbedBuilder();
  }

  static success(title?: string, description?: string): EmbedBuilder {
    return new EmbedBuilder().setSuccess(title, description);
  }

  static error(title?: string, description?: string): EmbedBuilder {
    return new EmbedBuilder().setError(title, description);
  }

  static info(title?: string, description?: string): EmbedBuilder {
    return new EmbedBuilder().setInfo(title, description);
  }

  static warning(title?: string, description?: string): EmbedBuilder {
    return new EmbedBuilder().setWarning(title, description);
  }

  static primary(title?: string, description?: string): EmbedBuilder {
    return new EmbedBuilder().setPrimary(title, description);
  }

  setPrimary(title?: string, description?: string): this {
    this.embed
      .setColor(EmbedBuilder.colors.primary)
      .setTitle(title ?? null)
      .setDescription(description ?? null);
    return this;
  }

  setSuccess(title?: string, description?: string): this {
    this.embed
      .setColor(EmbedBuilder.colors.success)
      .setTitle(title ?? null)
      .setDescription(description ?? null);
    return this;
  }

  setWarning(title?: string, description?: string): this {
    this.embed
      .setColor(EmbedBuilder.colors.warning)
      .setTitle(title ?? null)
      .setDescription(description ?? null);
    return this;
  }

  setError(title?: string, description?: string): this {
    this.embed
      .setColor(EmbedBuilder.colors.error)
      .setTitle(title ?? null)
      .setDescription(description ?? null);
    return this;
  }

  setInfo(title?: string, description?: string): this {
    this.embed
      .setColor(EmbedBuilder.colors.info)
      .setTitle(title ?? null)
      .setDescription(description ?? null);
    return this;
  }

  // ── Author ───────────────────────────────────────────

  setAuthor(name: string, url?: string, iconURL?: string): this {
    this.embed.setAuthor({ name, url, iconURL });
    return this;
  }

  // ── Body ─────────────────────────────────────────────

  setBody(title: string, description: string, url?: string): this {
    this.embed.setTitle(title).setDescription(description);
    if (url) this.embed.setURL(url);
    return this;
  }

  // ── Images ───────────────────────────────────────────

  setImageUrl(url: string): this {
    this.embed.setImage(url);
    return this;
  }

  setThumbnailUrl(url: string): this {
    this.embed.setThumbnail(url);
    return this;
  }

  // ── Footer ───────────────────────────────────────────

  setFooter(text: string, iconURL?: string, timestamp?: Date | boolean): this {
    this.embed.setFooter({ text, iconURL });
    if (timestamp) {
      this.embed.setTimestamp(timestamp === true ? new Date() : timestamp);
    }
    return this;
  }

  // ── Fields ───────────────────────────────────────────

  addInlineField(name: string, value: string, inline?: boolean): this {
    this.embed.addFields({ name, value, inline: inline ?? true });
    return this;
  }

  addBlankField(inline?: boolean): this {
    this.embed.addFields({ name: "\u200B", value: "\u200B", inline: inline ?? false });
    return this;
  }

  // ── Buttons ──────────────────────────────────────────

  addButton(label: string, customId: string, style?: ButtonStyle): this {
    this.buttons.push({ label, customId, style });
    return this;
  }

  addLinkButton(label: string, url: string): this {
    this.buttons.push({ label, url, customId: "", style: ButtonStyle.Link });
    return this;
  }

  // ── Color ────────────────────────────────────────────

  setColor(color: ColorResolvable): this {
    this.embed.setColor(color);
    return this;
  }

  // ── Build ────────────────────────────────────────────

  getEmbed(): DiscordEmbedBuilder {
    return DiscordEmbedBuilder.from(this.embed);
  }

  toMessageOptions() {
    const components: ActionRowBuilder<MessageActionRowComponentBuilder>[] = [];

    if (this.buttons.length > 0) {
      const row = new ActionRowBuilder<MessageActionRowComponentBuilder>();

      for (const btn of this.buttons) {
        const button = new ButtonBuilder()
          .setLabel(btn.label)
          .setStyle(btn.style ?? ButtonStyle.Primary);

        if (btn.url) {
          button.setURL(btn.url);
        } else {
          button.setCustomId(btn.customId);
        }

        if (btn.disabled) button.setDisabled(true);
        row.addComponents(button);
      }

      components.push(row);
    }

    return {
      embeds: [this.getEmbed()],
      components,
    };
  }
}
