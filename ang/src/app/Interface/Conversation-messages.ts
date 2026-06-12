import { Messages } from "./Messages";

export interface ConversationMessage {
  messages?: Messages[];
  name: string;
  convId: string;
  userId: number;
}
