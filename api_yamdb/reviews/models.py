from django.utils import timezone
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from users.models import User
from .validators import validate_year

now = timezone.now()


class Category(models.Model):
    """Категории произведений"""
    name = models.CharField(
        max_length=256,
        verbose_name='Категория',
        unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Жанры произведений"""
    name = models.CharField(
        max_length=256,
        verbose_name='Жанр',
        unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Произведения"""
    name = models.CharField(max_length=200, verbose_name='Произведение')
    year = models.PositiveSmallIntegerField(
        verbose_name='Дата выхода',
        validators=[validate_year],
        db_index=True)
    description = models.CharField(max_length=200, blank=True)
    genre = models.ManyToManyField(Genre, blank=True, related_name='titles')
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='titles')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE)
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'

    def __str__(self):
        return f'{self.title}, жанр - {self.genre}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Заголовок ревью',
        related_name='reviews'
    )
    text = models.TextField(
        verbose_name='Текст Ревью',
        blank=False,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор ревью',
        related_name='reviews'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(1, 'Допустимы значения от 1 до 10'),
            MaxValueValidator(10, 'Допустимы значения от 1 до 10')
        ]
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Ревью'
        verbose_name_plural = 'Ревью'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review'
            ),
        ]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Комментарий к ревью',
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        blank=False,
        help_text='Оставьте ваш комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
