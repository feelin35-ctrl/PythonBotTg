import StartNode from './StartNode';
import MessageNode from './MessageNode';
import ImageNode from './ImageNode';
import ButtonNode from './ButtonNode';
import InlineButtonNode from './InlineButtonNode';
import EndNode from './EndNode';
import ConditionNode from './ConditionNode';
import MenuNode from './MenuNode';
import FileNode from './FileNode';
import NLPResponseNode from './NLPResponseNode';
import DelayNode from './DelayNode';
import { ContextMenu } from './ContextMenu';
import { EditableNode } from './EditableNode';

export const nodeTypes = {
  start: StartNode,
  message: MessageNode,
  image: ImageNode,
  button: ButtonNode,
  inline_button: InlineButtonNode,
  end: EndNode,
  condition: ConditionNode,
  menu: MenuNode,
  file: FileNode,
  nlp_response: NLPResponseNode,
  delay: DelayNode,
};

// Добавляем отладочный вывод
console.log('Registered node types:', nodeTypes);
console.log('Available node types:', Object.keys(nodeTypes));

export { ContextMenu };
export { EditableNode };