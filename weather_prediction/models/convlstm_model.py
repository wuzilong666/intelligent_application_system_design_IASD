"""
ConvLSTM 模型
用于时空序列预测
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import config
from utils.helpers import log_message


class ConvLSTMModel:
    """ConvLSTM 天气预测模型"""
    
    def __init__(self, input_shape=None):
        """
        初始化模型
        
        参数:
            input_shape: 输入形状 (时间步, 高度, 宽度, 通道数)
        """
        self.input_shape = input_shape or config.CONVLSTM_CONFIG["input_shape"]
        self.model = None
        self.history = None
        log_message("ConvLSTM模型初始化")
    
    def build_model(self):
        """构建ConvLSTM模型"""
        log_message("开始构建ConvLSTM模型")
        
        # 输入层
        inputs = layers.Input(shape=self.input_shape)
        
        # ConvLSTM2D 层
        x = inputs
        for i, filters in enumerate(config.CONVLSTM_CONFIG["filters"]):
            return_sequences = (i < len(config.CONVLSTM_CONFIG["filters"]) - 1)
            
            x = layers.ConvLSTM2D(
                filters=filters,
                kernel_size=config.CONVLSTM_CONFIG["kernel_size"],
                padding='same',
                return_sequences=return_sequences,
                activation='relu',
                name=f'convlstm_{i+1}'
            )(x)
            
            x = layers.BatchNormalization()(x)
            x = layers.Dropout(config.CONVLSTM_CONFIG["dropout"])(x)
        
        # 输出层
        # 预测下一个时间步的天气图
        outputs = layers.Conv2D(
            filters=3,  # 3个通道：温度、湿度、气压
            kernel_size=(3, 3),
            padding='same',
            activation='sigmoid',
            name='output'
        )(x)
        
        # 创建模型
        self.model = keras.Model(inputs=inputs, outputs=outputs, name='ConvLSTM_Weather')
        
        # 编译模型
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=config.CONVLSTM_CONFIG["learning_rate"]),
            loss='mse',
            metrics=['mae']
        )
        
        log_message("ConvLSTM模型构建完成")
        return self.model
    
    def train(self, X_train, y_train, X_val=None, y_val=None, epochs=50, batch_size=32):
        """
        训练模型
        
        参数:
            X_train: 训练数据
            y_train: 训练标签
            X_val: 验证数据
            y_val: 验证标签
            epochs: 训练轮数
            batch_size: 批次大小
        """
        if self.model is None:
            self.build_model()
        
        log_message(f"开始训练模型，epochs={epochs}")
        
        # 回调函数
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=10,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss' if X_val is not None else 'loss',
                factor=0.5,
                patience=5
            )
        ]
        
        # 训练
        validation_data = (X_val, y_val) if X_val is not None else None
        
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        log_message("模型训练完成")
        return self.history
    
    def predict(self, X, return_uncertainty=False, num_samples=100):
        """
        预测
        
        参数:
            X: 输入数据
            return_uncertainty: 是否返回不确定性
            num_samples: 蒙特卡洛采样次数
            
        返回:
            预测结果（如果return_uncertainty=True，还包括标准差）
        """
        if self.model is None:
            raise ValueError("模型未构建或加载")
        
        if not return_uncertainty:
            # 直接预测
            predictions = self.model.predict(X)
            return predictions
        else:
            # 蒙特卡洛dropout预测（用于不确定性量化）
            log_message(f"使用蒙特卡洛方法进行{num_samples}次采样")
            
            # 启用dropout进行多次预测
            predictions_list = []
            for _ in range(num_samples):
                pred = self.model(X, training=True)  # training=True启用dropout
                predictions_list.append(pred.numpy())
            
            predictions_array = np.array(predictions_list)
            
            # 计算均值和标准差
            mean_prediction = np.mean(predictions_array, axis=0)
            std_prediction = np.std(predictions_array, axis=0)
            
            return mean_prediction, std_prediction
    
    def save_model(self, filepath=None):
        """
        保存模型
        
        参数:
            filepath: 保存路径
        """
        if filepath is None:
            filepath = f"{config.MODEL_DIR}/convlstm_model.h5"
        
        self.model.save(filepath)
        log_message(f"模型已保存到 {filepath}")
    
    def load_model(self, filepath=None):
        """
        加载模型
        
        参数:
            filepath: 模型路径
        """
        if filepath is None:
            filepath = f"{config.MODEL_DIR}/convlstm_model.h5"
        
        self.model = keras.models.load_model(filepath)
        log_message(f"模型已从 {filepath} 加载")
    
    def summary(self):
        """打印模型摘要"""
        if self.model is None:
            self.build_model()
        return self.model.summary()


if __name__ == "__main__":
    # 测试代码
    model = ConvLSTMModel()
    model.build_model()
    model.summary()
    
    # 创建测试数据
    X_test = np.random.rand(10, 10, 64, 64, 3)
    y_test = np.random.rand(10, 64, 64, 3)
    
    print(f"\n测试数据形状:")
    print(f"  输入: {X_test.shape}")
    print(f"  输出: {y_test.shape}")
    
    # 测试预测
    predictions = model.predict(X_test[:2])
    print(f"\n预测结果形状: {predictions.shape}")
