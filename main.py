import numpy as np
import scipy as sp
from scipy import misc, ndimage
from copy import deepcopy as dc
import os
import cv2
import random



class Block(object):
    '''
    class that stores the blocks and is used to help track the block itself
    There is an intent to add more code to block eventually but right now
    it is more of a stub class.

    Attributes
        beginning_x = the first x coordinate of this block
        end_x       = the last x coordinate of this block
        beginning_y = the first y coordinate of this block
        end_y       = the last y coordinate of this block
        id_num      = currently not in use
    '''
    def __init__(self, beginning_x, end_x, beginning_y, end_y,id_num=0):

        self.beg_x = beginning_x
        self.end_x =  end_x
        self.beg_y = beginning_y
        self.end_y = end_y
        self.changed = False
        self.id = id_num


    def __str__(self):
        return "[{0}:{1}, {2}:{3}]".format(self.beg_y, self.end_y, self.beg_x, self.end_x)


class Image(object):
    '''
    Class that contains the image and functions to use upon the image


    Attributes
        loc        = Location of image
        block_size = tuple containing size of block
        rand       = Controls how often a block sorts. Function pulls a random number and if it is greater than rand, some action will happen
        rand_range = This controls how far something can be away in random actions
    '''

    def __init__(self, loc, block_size,rand=0.5, rand_range=0):
        self.loc = loc
        self.image = ndimage.imread('images/{0}'.format(loc))
        self.block_size = block_size
        self.blocks = []
        self.rand = rand
        self.rand_range = rand_range
        self.actions = ''
        self.metrics = ''

        
    def save(self, other_location=''):
        ##saves image
        if other_location != '':
            misc.imsave(other_location, self.image)
        else:
            if not os.path.isdir('outputs/'):
                os.mkdir('outputs/')
            misc.imsave('outputs/{0}'.format(self.loc), self.image)


    def _is_right_size(self):
        
        ##Determine if we can evenly cut up the image
        x = self.image.shape[1] % self.block_size[1]
        y = self.image.shape[0] % self.block_size[0]
        if x != 0:
            return False
        if y != 0:
            return False
        return True


    def _get_dims(self, current, block_size):
        ## gets the correct size for our block choice
        left_over = current % block_size
        if left_over == 0:
            return 0
        return block_size - left_over
        
        
    def _fix_image(self):
        dy = self._get_dims(self.image.shape[0], self.block_size[0])
        dx = self._get_dims(self.image.shape[1], self.block_size[1])       
        self.image = cv2.copyMakeBorder(self.image,0, dy, 0, dx, cv2.BORDER_WRAP)
        

    def get_blocks(self):

        right = self._is_right_size()
        if not right:
            self._fix_image()
        block_y, block_x = self.block_size
        i, j = 0, 0
        ## this is what we will use to count blocks
        num_y = self.image.shape[0] / block_y
        num_x = self.image.shape[1] / block_x
        if num_y == 0 or num_x == 0:
            print 'oops'
        for y in range(0, num_y):
            i = 0
            for x in range(0, num_x):
                self.blocks.append(Block(i, i+block_x, j, j+block_y))
                
                i = i + block_x
            j = j + block_y
                
       
    def random_switch(self):
        num = len(self.blocks)
        for i in range(0, num):
            block_1 = self.blocks[i]
            if not block_1.changed:
                r = random.uniform(0, 1)
                if r > self.rand:
                    counter = 0
                    while True:
                        ## need to think about what happens if I've switched almost everything
                        if self.rand_range == 0:
                            block_2 = self.blocks[random.randint(0, num-1)]
                        else:
                            r_start = i -  self.rand_range
                            r_end = i + self.rand_range
                            if r_start < 0:
                                r_start = 0
                            if r_end > num - 1:
                                r_end = num -1
                            block_2 = self.blocks[random.randint(r_start, r_end)]
                        counter += 1
                        if not block_2.changed:
                            block_2.changed = True
                            self.blocks[i].changed = True
                            temp2 = dc(self.image[block_2.beg_y:block_2.end_y, block_2.beg_x:block_2.end_x])
                            self.image[block_2.beg_y:block_2.end_y, block_2.beg_x:block_2.end_x] = self.image[block_1.beg_y:block_1.end_y, block_1.beg_x:block_1.end_x]
                            self.image[block_1.beg_y:block_1.end_y, block_1.beg_x:block_1.end_x] = temp2
                            break
                        if counter > 15:
                            break


    def random_copy(self):
        num = len(self.blocks)
        for i in range(0, num):
            block_1 = self.blocks[i]
            if not block_1.changed:
                r = random.uniform(0, 1)
                if r > self.rand:
                    counter = 0
                    while True:
                        ## need to think about what happens if I've switched almost everything
                        if self.rand_range == 0:
                            block_2 = self.blocks[random.randint(0, num-1)]
                        else:
                            r_start = i -  self.rand_range
                            r_end = i + self.rand_range
                            if r_start < 0:
                                r_start = 0
                            if r_end > num - 1:
                                r_end = num -1
                            block_2 = self.blocks[random.randint(r_start, r_end)]
                        counter += 1
                        if not block_2.changed:
                            self.blocks[i].changed = True
                            temp2 = self.get_chunk(block_2)
                            self.assign_chunk(block_1, temp2)
                            break
                        if counter > 15:
                            break


    def get_chunk(self, block):
        return self.image[block.beg_y:block.end_y, block.beg_x:block.end_x]


    def get_chunks(self, blocks):
        chunks = []
        for i in blocks:
            chunks.append(self.get_chunk(i))
        return chunks


    def swap(self, block_1, block_2, chunk_1, chunk_2):
        self.assign_chunks([block_1, block_2], [chunk_2, chunk_1])


    def assign_chunk(self, block, values):
        ''' assigns the values in values to the block's coordinates in self.image'''
        self.image[block.beg_y:block.end_y, block.beg_x:block.end_x] = values


    def assign_chunks(self, blocks, values):
        for i in range(0, len(blocks)):
            self.assign_chunk(blocks[i], values[i])


###################
#### FUNCTIONS ####
###################


class Actions(object):
    '''
        These are actions that can be done upon the image
        Attribute
            image = the image class that
            
    '''

    def magic(self,img, metric, action):
        num = len(img.blocks)
        for block_index in range(0, num):
            r = random.uniform(0,1)
            if r > img.rand:
                block_1 = img.blocks[block_index]
                if not block_1.changed:
                    ##Find block to perform magic with
                    ## perform an action on there. Maybe its swapping, Maybe its averaging.
                    new_index = metric(img, block_index)
                    block_2 = img.blocks[new_index]
                    [chunk_1, chunk_2] = img.get_chunks([block_1, block_2])
                    action(img, block_1, block_2, chunk_1, chunk_2)


    def swap_colors(self,img):
        color_1 = dc(img.image[:,:,0])
        color_2 = dc(img.image[:,:,1])
        img.image[:,:,0] = color_2
        img.image[:,:,1] = color_1


    def swap_single_order(self,img):
        counter = 0
        next_color = 1
        y, x, t = img.image.shape
        for i in range(0,y):
            for j in range(0,x):
                v1 = dc(img.image[i, j, counter])
                v2 = dc(img.image[i, j, next_color])
                img.image[i, j, counter] = v2
                img.image[i, j, next_color] = v1
                counter = (counter + 1) % 3
                next_color = (next_color + 1) % 3
                
                    


################
### ACTIONS  ###
################
    def average(self,img,  b1, b2, c1, c2):
        '''
        averages two blocks and set block one to that value
        '''
        average_chunk_1 = cv2.addWeighted(c1, 0.5, c2, 0.5, 0)
        b2.changed = False
        img.assign_chunk(b1, average_chunk_1)


    def average_and_swap(self,img, b1, b2, c1, c2):
        '''
        Averages two blocks and then swaps the averaged block with the
        non averaged block
        
    	'''
        average_chunk_1 = cv2.addWeighted(c1, 0.50, c2, 0.50, 0)
        img.swap(b1, b2, average_chunk_1, c2)
        
        
#####################
##### METRICS #######
#####################

class Metrics(object):

        
    def ssd(self, img, block_ind, gtlt):
        '''
        uses the block index and returns the index of the most block that is
        most like it or most dislike it. There are two wrapper functions that
        call this and will either choose gt or lt
        '''
        block = img.blocks[block_ind]
        most_like_or_dislike = 0
        if gtlt == 'gt':
            similarity = -1
        else:
            similarity = 999999
        for i in range(len(img.blocks)):
            if i != block_ind:
                second_block = img.blocks[i]
                ##make sure to not switch images twice
                ##without you might switch and switch back
                if second_block.changed == False:
                    chunk_1 = img.get_chunk(block)
                    chunk_2 = img.get_chunk(second_block)
                    ssd = np.sum((chunk_1[:,:,:] - chunk_2[:,:,:])**2)
                    if gtlt == 'gt':
                        if ssd > similarity:
                            similarity = dc(ssd)
                            most_like_or_dislike = dc(i)
                    else:
                        if ssd < similarity:
                            similarity = dc(ssd)
                            most_like_or_dislike = dc(i)
                        
        block.changed = True
        ##This will make sure that the second block is not used again
        ##However if you want to maybe use that block in the future
        ##Use the returned index to change set changed back to False
        img.blocks[most_like_or_dislike].changed = True       
        return most_like_or_dislike
                    
            
    def ssd_similar(self, img, block_ind):
        '''
        Takes in block index and then calls self.ssd with lt option.
        This will try to swap blocks that are most like each other hence
        we compare less than to get the smallest difference
        '''
        return self.ssd(img, block_ind, 'lt')


    def ssd_dissimilar(self, img, block_ind):
        '''
        Takes in block index and then calls self.ssd with gt option.
        This will try to swap blocks that are most dissimilar each other hence
        we compare greater than to get the largest difference
        '''
        return self.ssd(img, block_ind, 'gt')



                    
                    
                    

if __name__ == '__main__':
    i_path = 'me.jpg'
    img1 = Image(i_path, (150, 150), .75, 20)
    img1.get_blocks()
    metrics = Metrics()
    actions = Actions()
    metric = metrics.ssd_similar
    action = actions.average_and_swap
    actions.magic(img1, metric, action)
    img1.save()

    
