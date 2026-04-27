from coze_coding_dev_sdk.database import Base

from typing import Optional
import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Double, Integer, Numeric, PrimaryKeyConstraint, Table, Text, text, Float, String, Index, ForeignKey, func
from sqlalchemy.dialects.postgresql import OID
from sqlalchemy.orm import Mapped, mapped_column

class HealthCheck(Base):
    __tablename__ = 'health_check'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='health_check_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))


class UserProfile(Base):
    """用户档案表 - 存储用户的基础数据"""
    __tablename__ = "user_profile"
    __table_args__ = (
        Index("ix_user_profile_city", "city"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    height: Mapped[float] = mapped_column(Float, nullable=False, comment="身高(cm)")
    weight: Mapped[float] = mapped_column(Float, nullable=False, comment="体重(kg)")
    body_fat_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="体脂率(%)")
    body_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="体型")
    skin_tone: Mapped[str] = mapped_column(String(50), nullable=False, comment="肤色")
    style_preference: Mapped[str] = mapped_column(String(100), nullable=False, comment="风格偏好")
    city: Mapped[str] = mapped_column(String(100), nullable=False, comment="所在城市")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), onupdate=func.now(), nullable=True)


class Wardrobe(Base):
    """衣橱表 - 存储用户的衣物信息"""
    __tablename__ = "wardrobe"
    __table_args__ = (
        Index("ix_wardrobe_category", "category"),
        Index("ix_wardrobe_season", "season"),
        Index("ix_wardrobe_occasion", "occasion"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, comment="衣物类型(上衣/裤子/外套/鞋子/配饰)")
    color: Mapped[str] = mapped_column(String(50), nullable=False, comment="颜色")
    style: Mapped[str] = mapped_column(String(100), nullable=False, comment="风格")
    season: Mapped[str] = mapped_column(String(50), nullable=False, comment="适合季节(春夏秋冬/四季)")
    occasion: Mapped[str] = mapped_column(String(100), nullable=False, comment="适合场合(上班/约会/休闲/正式)")
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="详细描述")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), onupdate=func.now(), nullable=True)


class FitnessPlan(Base):
    """健身计划表 - 存储用户的健身计划"""
    __tablename__ = "fitness_plan"
    __table_args__ = (
        Index("ix_fitness_plan_goal", "goal"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    goal: Mapped[str] = mapped_column(String(100), nullable=False, comment="健身目标(减脂/增肌/塑形/维持)")
    target_weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="目标体重(kg)")
    weekly_workout_days: Mapped[int] = mapped_column(Integer, nullable=False, comment="每周训练天数")
    workout_duration: Mapped[int] = mapped_column(Integer, nullable=False, comment="每次训练时长(分钟)")
    intensity: Mapped[str] = mapped_column(String(50), nullable=False, comment="强度(低/中/高)")
    plan_content: Mapped[str] = mapped_column(Text, nullable=False, comment="健身计划详细内容")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), onupdate=func.now(), nullable=True)


class DietPlan(Base):
    """饮食计划表 - 存储用户的饮食计划"""
    __tablename__ = "diet_plan"
    __table_args__ = (
        Index("ix_diet_plan_goal", "goal"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    goal: Mapped[str] = mapped_column(String(100), nullable=False, comment="饮食目标(减脂/增肌/维持)")
    daily_calories: Mapped[int] = mapped_column(Integer, nullable=False, comment="每日目标热量(千卡)")
    protein_ratio: Mapped[float] = mapped_column(Float, nullable=False, comment="蛋白质占比(0-1)")
    carb_ratio: Mapped[float] = mapped_column(Float, nullable=False, comment="碳水化合物占比(0-1)")
    fat_ratio: Mapped[float] = mapped_column(Float, nullable=False, comment="脂肪占比(0-1)")
    plan_content: Mapped[str] = mapped_column(Text, nullable=False, comment="饮食计划详细内容")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), onupdate=func.now(), nullable=True)


class DailyDietLog(Base):
    """每日饮食记录表"""
    __tablename__ = "daily_diet_log"
    __table_args__ = (
        Index("ix_daily_diet_log_date", "log_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    log_date: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, comment="记录日期")
    meal_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="餐次(早餐/午餐/晚餐/加餐)")
    food_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="食物名称")
    calories: Mapped[float] = mapped_column(Float, nullable=False, comment="热量(千卡)")
    protein: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="蛋白质(g)")
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="备注")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=func.now(), nullable=False)


class DailyExerciseLog(Base):
    """每日锻炼记录表"""
    __tablename__ = "daily_exercise_log"
    __table_args__ = (
        Index("ix_daily_exercise_log_date", "log_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    log_date: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, comment="记录日期")
    exercise_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="运动名称")
    duration: Mapped[int] = mapped_column(Integer, nullable=False, comment="运动时长(分钟)")
    calories_burned: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="消耗热量(千卡)")
    intensity: Mapped[str] = mapped_column(String(50), nullable=False, comment="强度(低/中/高)")
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="备注")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=func.now(), nullable=False)


t_pg_stat_statements = Table(
    'pg_stat_statements', Base.metadata,
    Column('userid', OID),
    Column('dbid', OID),
    Column('toplevel', Boolean),
    Column('queryid', BigInteger),
    Column('query', Text),
    Column('plans', BigInteger),
    Column('total_plan_time', Double(53)),
    Column('min_plan_time', Double(53)),
    Column('max_plan_time', Double(53)),
    Column('mean_plan_time', Double(53)),
    Column('stddev_plan_time', Double(53)),
    Column('calls', BigInteger),
    Column('total_exec_time', Double(53)),
    Column('min_exec_time', Double(53)),
    Column('max_exec_time', Double(53)),
    Column('mean_exec_time', Double(53)),
    Column('stddev_exec_time', Double(53)),
    Column('rows', BigInteger),
    Column('shared_blks_hit', BigInteger),
    Column('shared_blks_read', BigInteger),
    Column('shared_blks_dirtied', BigInteger),
    Column('shared_blks_written', BigInteger),
    Column('local_blks_hit', BigInteger),
    Column('local_blks_read', BigInteger),
    Column('local_blks_dirtied', BigInteger),
    Column('local_blks_written', BigInteger),
    Column('temp_blks_read', BigInteger),
    Column('temp_blks_written', BigInteger),
    Column('shared_blk_read_time', Double(53)),
    Column('shared_blk_write_time', Double(53)),
    Column('local_blk_read_time', Double(53)),
    Column('local_blk_write_time', Double(53)),
    Column('temp_blk_read_time', Double(53)),
    Column('temp_blk_write_time', Double(53)),
    Column('wal_records', BigInteger),
    Column('wal_fpi', BigInteger),
    Column('wal_bytes', Numeric),
    Column('jit_functions', BigInteger),
    Column('jit_generation_time', Double(53)),
    Column('jit_inlining_count', BigInteger),
    Column('jit_inlining_time', Double(53)),
    Column('jit_optimization_count', BigInteger),
    Column('jit_optimization_time', Double(53)),
    Column('jit_emission_count', BigInteger),
    Column('jit_emission_time', Double(53)),
    Column('jit_deform_count', BigInteger),
    Column('jit_deform_time', Double(53)),
    Column('stats_since', DateTime(True)),
    Column('minmax_stats_since', DateTime(True))
)


t_pg_stat_statements_info = Table(
    'pg_stat_statements_info', Base.metadata,
    Column('dealloc', BigInteger),
    Column('stats_reset', DateTime(True))
)
