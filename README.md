# Content Management System
Trata-se de um sistema de linha de comando em que o usuário pode criar e gerenciar sites de conteúdo. Em cada Site podem ser publicados (ou agendados) Posts. Em cada Post, pode-se fazer comentários. Cada Site também conta com uma biblioteca de Mídias que podem ser usadas para construção dos Posts. 

## Como executar
```python
python main.py
```

>[!warning]
> Desenvolvido e testado com Python `3.13`.

## Funcionalidades implementadas
- [x] User Roles and Permissions
- [x] Content Creation and Editing
- [x] Comment and Review System
- [x] Media Library Management
- [x] Content Scheduling
- [x] Analytics and Reporting
- [x] Template and Design Customization
- [x] SEO Optimization Tools
- [x] Multi-Language Support
- [x] Social Media Integration

## Projeto do Modelo do Sistema (Objetos)
- **User**: Represents an user in the system
- **Site**: Represents a website that an user (owner) can create and other users can access
- **Post**: Represents the information available to an User in a Site
- **Content**: Represents information of a Post in a language. It is a list of ContentBlocks.
- **ContentBlock**: Represents a fraction of the information of a Post
- **TextBlock**: Represents a block of text that is part of a Post 
- **MediaBlock**: Represents a block containing a Media file that is part of a Post
- **CarouselBlock**: Represents a carousel of Medias thath can be placed in the Post body
- **MediaFile**: Represents a Media file and all their metadata (width, height, size in bytes, etc)
- ~~**VideoFile**: Represents a video file and their specific data~~
- ~~**ImageFile**: Represents an image file and their specific data~~
    - These subclasses are not really necessary, because there are not enough differences between them. The MediaFile class alone will suffice for this application. 
- **Permission**: Represents which Post/Site an User can access
- **Comment**: Represents a message that a User can leave on a Post
- **AnalyticsEntry**: Represents an action of an User that will be used to extract metrics
- **AnalyticsReport**: Represents a closed snapshot of metrics to present
- **SiteAnalyticsReport**: Represents a AnalyticsReport for a Site 
- **PostAnalyticsReport**: Represents a AnalyticsReport for a Post
- **Template**: Represents the way the a Site will be presented to the User
- **Language**: Represents a language that a User can write a Post or a Comment in
- **SocialMedia**: Represents a Social Media to which the User can share a Post
- **SocialMediaPost**: Represents the Post formatted to that Social Media.
- **FacebookPost** Represents the Post formatted to be Posted in Facebook. 
- **InstagramPost** Represents the Post formatted to be Posted in Instagram. 
- **TwitterPost** Represents the Post formatted to be Posted in Instagram. 

