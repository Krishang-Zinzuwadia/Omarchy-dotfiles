const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function fetchRealData() {
  try {
    console.log('Fetching real data from database...');
    
    // Fetch past papers with tags
    const pastPapers = await prisma.pastPaper.findMany({
      take: 15,
      include: {
        tags: true,
        author: true,
      },
      orderBy: {
        createdAt: 'desc'
      }
    });

    console.log(`Found ${pastPapers.length} past papers`);
    
    // Fetch notes with tags
    const notes = await prisma.note.findMany({
      take: 15,
      include: {
        tags: true,
        author: true,
      },
      orderBy: {
        createdAt: 'desc'
      }
    });

    console.log(`Found ${notes.length} notes`);

    // Fetch forum posts with tags
    const forumPosts = await prisma.forumPost.findMany({
      take: 15,
      include: {
        tags: true,
        author: true,
        comments: {
          include: {
            author: true
          }
        },
        votes: true
      },
      orderBy: {
        createdAt: 'desc'
      }
    });

    console.log(`Found ${forumPosts.length} forum posts`);

    // Fetch subjects
    const subjects = await prisma.subject.findMany({
      take: 15,
      include: {
        modules: true
      },
      orderBy: {
        name: 'asc'
      }
    });

    console.log(`Found ${subjects.length} subjects`);

    // Print sample data
    console.log('\n=== SAMPLE PAST PAPERS ===');
    pastPapers.slice(0, 3).forEach((paper, index) => {
      console.log(`${index + 1}. ${paper.title}`);
      console.log(`   Tags: ${paper.tags.map(tag => tag.name).join(', ')}`);
      console.log(`   Author: ${paper.author?.name || 'Unknown'}`);
      console.log(`   Created: ${paper.createdAt}`);
      console.log('');
    });

    console.log('\n=== SAMPLE NOTES ===');
    notes.slice(0, 3).forEach((note, index) => {
      console.log(`${index + 1}. ${note.title}`);
      console.log(`   Tags: ${note.tags.map(tag => tag.name).join(', ')}`);
      console.log(`   Author: ${note.author?.name || 'Unknown'}`);
      console.log(`   Created: ${note.createdAt}`);
      console.log('');
    });

    console.log('\n=== SAMPLE FORUM POSTS ===');
    forumPosts.slice(0, 3).forEach((post, index) => {
      console.log(`${index + 1}. ${post.title}`);
      console.log(`   Tags: ${post.tags.map(tag => tag.name).join(', ')}`);
      console.log(`   Author: ${post.author?.name || 'Unknown'}`);
      console.log(`   Votes: ${post.upvoteCount} up, ${post.downvoteCount} down`);
      console.log(`   Created: ${post.createdAt}`);
      console.log('');
    });

    console.log('\n=== SAMPLE SUBJECTS ===');
    subjects.slice(0, 3).forEach((subject, index) => {
      console.log(`${index + 1}. ${subject.name}`);
      console.log(`   Modules: ${subject.modules.length}`);
      console.log('');
    });

    // Check for CAT/FAT tags specifically
    const catTags = await prisma.tag.findMany({
      where: {
        OR: [
          { name: { contains: 'CAT' } },
          { name: { contains: 'FAT' } }
        ]
      }
    });

    console.log('\n=== CAT/FAT TAGS FOUND ===');
    catTags.forEach(tag => {
      console.log(`- ${tag.name}`);
    });

    return {
      pastPapers,
      notes,
      forumPosts,
      subjects,
      catTags
    };

  } catch (error) {
    console.error('Error fetching data:', error);
    return null;
  } finally {
    await prisma.$disconnect();
  }
}

fetchRealData().then((data) => {
  if (data) {
    console.log('\n✅ Successfully fetched real data!');
    console.log(`Total: ${data.pastPapers.length} papers, ${data.notes.length} notes, ${data.forumPosts.length} forum posts, ${data.subjects.length} subjects`);
  } else {
    console.log('\n❌ Failed to fetch data');
  }
});
