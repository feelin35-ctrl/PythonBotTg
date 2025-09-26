from blocks.base_block import BaseBlock
import logging

logger = logging.getLogger(__name__)

class ProductBlock(BaseBlock):
    def __init__(self, node_data):
        super().__init__(node_data)
        self.type = 'product_card'
        
        # Извлекаем данные карточки товара
        self.data = node_data.get('data', {})
        self.photo_url = self.data.get('photo_url', '')
        self.title = self.data.get('title', '')
        self.description = self.data.get('description', '')
        self.price = self.data.get('price', '')
        self.features = self.data.get('features', [])
        
    @staticmethod
    def get_block_type() -> str:
        return "product_card"
        
    def execute(self, bot, chat_id, **kwargs):
        """Отправляет карточку товара пользователю"""
        try:
            logger.info(f"Executing ProductBlock for chat {chat_id}")
            
            # Формируем сообщение с информацией о товаре
            message_text = self._format_product_message()
            
            # Отправляем фото, если есть
            if self.photo_url:
                try:
                    bot.send_photo(
                        chat_id=chat_id,
                        photo=self.photo_url,
                        caption=message_text,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Error sending photo: {e}")
                    # Если не удалось отправить фото, отправляем текстовое сообщение
                    bot.send_message(
                        chat_id=chat_id,
                        text=f"Изображение: {self.photo_url}\n\n{message_text}",
                        parse_mode='Markdown'
                    )
            else:
                # Если нет изображений, отправляем только текст
                bot.send_message(
                    chat_id=chat_id,
                    text=message_text,
                    parse_mode='Markdown'
                )
            
            logger.info(f"Product card sent successfully to chat {chat_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error in ProductBlock: {str(e)}")
            bot.send_message(
                chat_id=chat_id,
                text="❌ Произошла ошибка при отображении карточки товара"
            )
            return None
    
    def _format_product_message(self) -> str:
        """Форматирует данные товара в текст сообщения"""
        message_parts = []
        
        # Добавляем название
        if self.title:
            message_parts.append(f"*{self.title}*\n")
        
        # Добавляем описание
        if self.description:
            message_parts.append(f"{self.description}\n")
        
        # Добавляем цену
        if self.price:
            message_parts.append(f"*Цена:* {self.price}\n")
        
        # Добавляем характеристики
        if self.features:
            message_parts.append("*Характеристики:*\n")
            for feature in self.features:
                if isinstance(feature, dict) and 'key' in feature and 'value' in feature:
                    key = feature.get('key', '')
                    value = feature.get('value', '')
                    if key and value:
                        message_parts.append(f"• {key}: {value}\n")
                elif isinstance(feature, str):
                    message_parts.append(f"• {feature}\n")
        
        return "\n".join(message_parts).strip() if message_parts else "Карточка товара"